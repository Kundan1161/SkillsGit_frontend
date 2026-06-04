---
id: skillsgit-curated/stakeholder-update-writer
version: 1.0.0
name: Stakeholder Update Writer
description: Turn a project's recent activity into a tight weekly or monthly update for leadership — a one-screen status with health rating, key wins, risks, asks, and what is next.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [status-report, stakeholder-update, project-management, executive-communication, weekly-update, internal-comms]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 4000
trigger_keywords:
  - status update
  - weekly update
  - stakeholder update
  - project status
  - leadership update
  - exec update
  - status report
  - RAG status
  - monthly update
  - project update
  - sponsor report
example_invocations:
  - "Write the weekly update for our launch project based on this week's commits and the standup notes."
  - "Draft a monthly status for leadership — green/yellow/red — for the platform migration."
  - "Take these PR titles, the open risks, and the budget burn, and produce the sponsor update."
  - "I need to send the exec sponsor a one-screen update by Friday."
inputs:
  - name: project_name
    type: text
    required: true
    description: The name of the project the update is about, exactly as it appears in stakeholder communication.
  - name: activity
    type: text
    required: true
    description: The week's or month's activity — commits, shipped features, completed tasks, demos, decisions, customer interactions, blockers resolved. Bullets are fine; messy is fine.
  - name: risks_and_blockers
    type: text
    required: false
    description: Any known risks, blockers, or asks. If omitted, the skill flags this and asks the writer to confirm "no risks" before sending.
  - name: cadence
    type: choice
    required: false
    description: How often the update is sent. Affects length and tone.
    choices: [weekly, biweekly, monthly, ad_hoc]
  - name: audience
    type: text
    required: false
    description: Who reads this update. Defaults to "executive sponsor and adjacent leaders." Specify more tightly when the audience is technical, customer-facing, or board-level.
  - name: previous_update
    type: text
    required: false
    description: Last week's or last month's update. Used so the new one references resolved items, shows trend on the health rating, and avoids restating context.
outputs:
  - name: update
    type: markdown
    description: The structured update — header with health rating, TL;DR, this period, next period, risks, asks, metrics — sized to one screen.
  - name: long_version
    type: markdown
    description: An optional longer variant for project sponsors who want full detail — adds a "since last update" diff section and a metrics block.
  - name: changes_log
    type: markdown
    description: A list of items that changed since the previous update, including any items where the health rating changed.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Stakeholder Update Writer

## When to use

Use this skill when the asker owns a project and owes a written update to people who are not in the day-to-day — an executive sponsor, a steering committee, a partner team's lead, or a board observer. The output is a one-screen artifact that the reader can absorb in under a minute and a longer variant they can drill into when they have ten.

It is **not** the right tool when:

- The audience is the project team itself. Use a standup or a retro skill; this one strips the texture that teammates need.
- The output is a pitch for new funding. Use a business-case or pitch-deck skill; status updates are not the place to make a case.
- The output is a postmortem or incident report. Those have different shapes, different audiences, and different accountability lines.
- The asker has nothing to report. Decline politely and recommend a half-line "no material change since last update" instead of fabricating content.

Engage when the asker can supply a period's worth of activity (a week, two weeks, or a month) and the reader is expected to skim, not study.

## How to apply

Run the methodology in four phases. Each phase removes a class of update defect.

### Phase 1 — Frame the period and set the health rating

1. **Confirm the period.** What window does this update cover? If `cadence` is set, derive the window from today's date and the cadence. Otherwise infer from the activity input: if the items span a week, the window is a week. State the window explicitly in the header so the reader knows what they are absorbing.
2. **State the health rating.** Choose one of three signals — *on track*, *at risk*, *off track*. Map them to common color cues for readers who expect them (green / yellow / red) but never lead with the color alone; the color is the cue, the word is the meaning. Use the word in the header.
3. **Apply the rating rubric strictly.**
   - *On track:* delivery date is unchanged, no new material risks, no asks of leadership, work is proceeding within the planned scope.
   - *At risk:* delivery date is unchanged but one or more material risks have emerged, OR an ask of leadership is pending, OR a near-miss occurred this period.
   - *Off track:* delivery date has slipped, OR scope has been cut to preserve date, OR a hard blocker has not been cleared after one period.
4. **Move only one notch at a time without justification.** If the rating changed from on track to off track in a single period, the update must explain what changed — readers lose trust in updates that swing more than one notch without a clear narrative.
5. **Show the trend.** If `previous_update` is supplied, show the rating from last period next to this period: "On track (was: On track)" or "At risk (was: On track — changed because…)." Trend is half the signal.
6. **Refuse to over-report green.** Three consecutive "all green, nothing to flag" updates are a credibility issue, not a virtue. If the asker has truly nothing to flag, the update can be shorter — but include at least one item under "what's next" so the reader knows the work is alive.

### Phase 2 — Compose the one-screen update

7. **Header block.** Three lines: project name; period covered ("Week of 2026-05-12" or "April 2026"); health rating with trend.
8. **TL;DR.** One paragraph, three to five sentences. What is the project's state in one breath? Mention the date, the rating, the single most important thing that happened, the single most important thing coming up, and any ask. A reader who reads only the TL;DR should be able to act on it.
9. **This period: highlights.** Three to five bullets. Each bullet is one sentence, verb-led, past tense. Quantify where possible ("shipped 12 fixes" beats "shipped a lot of fixes"). Order by importance to the reader, not chronologically.
10. **Skip the cruft.** "Continued to work on" is not a highlight. "Started thinking about" is not a highlight. A highlight is a thing that changed in the world: a feature shipped, a customer signed, a hire made, a risk closed. If the period had no such items, write "low-output period; see what's next."
11. **Next period: priorities.** Three to five bullets. Each bullet is one sentence, verb-led, future tense, with a target. "Finish the data migration by 2026-05-21" beats "continue migration work." If a priority is conditional ("if QA passes, ship to prod"), say so plainly.
12. **Risks.** Zero to three risks. Each is *what could go wrong*, *how likely*, *impact if it lands*, and *mitigation*. Keep the language calibrated: "could slip by a week" is not the same as "will miss the target." Distinguish. Cap at three; an update with eight risks is a postmortem in disguise.
13. **Asks.** Zero to two asks. An ask is something the reader can give the writer that unblocks the work — a decision, a person, a budget approval, an introduction. Frame each ask as a question or a sentence the reader can say "yes" to. Date-stamp asks: "By 2026-05-21" is a complete ask; "soon" is not.
14. **Metrics.** Optional; include only if a metric tells the reader something the prose has not. Pick at most three. Each row: metric name, current value, prior value, target value, trend arrow. Resist the urge to put every dashboard chart in the update.
15. **Length budget.** Aim for under 250 words in the one-screen version, exclusive of the optional metrics table. If you cannot say it in 250 words, the long version is the right place for the rest.

### Phase 3 — Compose the long version (optional)

16. **Reuse the one-screen as the lead.** The long version is not a different report; it is the one-screen plus appendices. The reader who has time will start at the top and stop reading when they have what they need.
17. **Add a "since last update" diff.** Items resolved: list. Items now in flight: list. Items dropped: list with reasons. This section is the audit trail for the project's evolution.
18. **Add a detail section per workstream.** If the project has named subprojects or workstreams, give each one a paragraph under a sub-heading. Same structure: this period, next period, risks specific to that stream.
19. **Add the people block.** Optional. Joiners, leavers, role changes, on-call swaps. Skip if nothing changed.
20. **Add the calendar block.** Optional. Upcoming milestones with target dates, in a small table. Mark slipped milestones explicitly; do not silently update dates.
21. **Cap the long version too.** Under 700 words. If the project demands more, it is time for a deck or a quarterly review, not a longer status email.

### Phase 4 — Self-review and produce the auxiliary outputs

22. **Re-read as the busiest reader.** Could they get the gist in 20 seconds? Is the rating the first thing they see after the project name? Is there an unambiguous "what changed since last week"?
23. **Re-read as the most-concerned reader.** A skeptic sees the green rating; do they have what they need to trust it? Are the risks proportionate, calibrated, and named with their owners?
24. **Re-read as the writer's future self.** Six months from now, would this update help reconstruct what happened? If a key decision is missing, add a one-liner.
25. **Strip flattery and hedging.** Cut "exciting," "thrilled," "delighted," "I just wanted to share." Cut "I think," "hopefully," "we're trying to." If you are reporting fact, report it; if you are reporting uncertainty, name the uncertainty and its drivers.
26. **Verify the asks are askable.** An ask of leadership that requires reading 30 pages is not an ask, it is a referral. Pre-summarize anything the reader needs to act.
27. **Verify the metrics tie out.** Each metric should match the source numbers. If the source disagrees with itself (the activity says "shipped 12 fixes," the metric row says "10"), reconcile or flag.
28. **Produce the changes log.** A separate output listing every item that changed *between this update and the prior one*: rating changes, slipped dates, closed risks, completed asks, dropped scope. The changes log is the asker's record; do not include it in the update unless the audience explicitly wants it.
29. **Confidence-tag uncertain claims.** If a delivery date in the update is uncertain ("aiming for 2026-06-15"), say so. Better to write "target 2026-06-15 (low confidence — depends on Acme integration)" than to commit and miss.
30. **Suggest the subject line.** Output a one-line subject suitable for email or chat. Format: `[Project name] — [Period] — [Rating]`. Example: `Atlas migration — Week of 2026-05-12 — At risk`. This is the most-read part of the update.

## Inputs

- **`project_name`** — required. Use the exact name leadership recognizes. Internal codenames are fine if that is what the audience uses; otherwise resolve to the public name.
- **`activity`** — required. Bullets, paragraphs, or a paste-dump are all acceptable. More structure produces a tighter update, but the skill handles unstructured input by tagging each item.
- **`risks_and_blockers`** — optional. If omitted, the skill includes a "no risks reported" note and recommends the asker confirm before sending; risks are easier to omit than to surface, and an update that pretends there are none erodes trust.
- **`cadence`** — optional. Defaults to weekly. The cadence affects length and tone: monthly updates can be longer and more reflective; weekly updates are tighter and more operational.
- **`audience`** — optional. Defaults to "executive sponsor and adjacent leaders." Other useful values: "board observer" (tighter, more neutral, no internal jargon), "engineering leadership" (preserves technical specifics), "customer steering committee" (drops internal politics, surfaces customer-visible items).
- **`previous_update`** — optional but strongly recommended after the first one. Without it, the skill cannot show trend on the health rating and cannot produce a clean changes log.

## Outputs

- **`update`** — the one-screen update, under 250 words plus the optional metrics table.
- **`long_version`** — the longer variant, under 700 words, with workstream detail and a since-last-update diff. Optional.
- **`changes_log`** — the audit trail of what changed between this update and the prior one. Not included in `update` unless the audience asks for it.

## Examples

### Example 1 — Weekly update for an engineering platform migration

**Inputs.** `project_name`: "Atlas migration." `activity`: a list of merged PRs, two demos, one customer pilot kickoff, and one production incident. `risks_and_blockers`: "Acme integration ETA slipping by ~1 week; QA capacity tight." `cadence`: weekly. `previous_update`: last week's, which was rated on track.

**Output highlights.**

- **Subject.** `Atlas migration — Week of 2026-05-12 — At risk`
- **Header.** Project name; period; "At risk (was: On track — changed because Acme integration slipped and QA capacity tight)."
- **TL;DR.** Four sentences. Names the migration is now 80% through the back-end cutover, that the Acme integration slipped, that there is one ask of leadership (decision on the Acme fallback), and that the next milestone is the staging cutover on 2026-05-20.
- **This period.** Five bullets: merged 14 PRs, completed the API gateway cutover, ran two customer demos, kicked off the Acme pilot, resolved a 22-minute production incident (link).
- **Next period.** Four bullets, each verb-led with a date.
- **Risks.** Two: Acme integration slip; QA capacity. Each calibrated and mitigation-stated.
- **Asks.** One: "Decide by 2026-05-19 whether to delay the cutover by a week or proceed with the Acme fallback path."

### Example 2 — Monthly update for a product launch

**Inputs.** `project_name`: "Insights v2 launch." `activity`: month's worth of bullets — product reviews, beta signups, content marketing milestones, two postponed deliverables. `cadence`: monthly. `audience`: "executive sponsor and adjacent leaders." `previous_update`: April's, rated on track.

**Output highlights.**

- **Subject.** `Insights v2 launch — April 2026 — At risk`
- **Header.** Rating: At risk (was: On track — changed because two deliverables postponed).
- **TL;DR.** Five sentences. States the launch date target, the two slipped deliverables, the recovery plan, and the one ask: an additional designer for two weeks.
- **This period.** Five bullets, including the postponements stated plainly with their causes.
- **Next period.** Five bullets, all with dates.
- **Risks.** Two, calibrated.
- **Asks.** One: "Two-week loan of a designer from the Marketing team to recover the content-card visuals."
- **Metrics.** Three rows: beta signups (current 412, prior 280, target 600); launch readiness checklist completion (62%, 48%, 100% by 2026-06-15); critical bugs open (4, 6, 0 by 2026-06-01).

### Example 3 — Ad-hoc update after a near-miss

**Inputs.** `project_name`: "Settlements pipeline." `activity`: a description of a near-miss — a deploy that almost shipped a data corruption bug, caught at the staging step. `risks_and_blockers`: "Test coverage gap in the affected module." `cadence`: ad_hoc. No `previous_update` supplied.

**Output highlights.**

- **Subject.** `Settlements pipeline — Ad-hoc update — At risk`
- **Header.** Rating: At risk. Trend not shown (no prior update supplied).
- **TL;DR.** Three sentences. Names the near-miss, the catch, and the immediate test-coverage commitment.
- **This period.** Three bullets describing what happened and what was caught when.
- **Next period.** Two bullets, including a coverage-fill milestone and a postmortem date.
- **Risks.** One: the same gap likely exists in two adjacent modules, scoped for review.
- **Asks.** None.
- **Confidence note.** "Root cause confirmed; scope of similar gaps in adjacent modules is medium-confidence and will be revised after the postmortem on 2026-05-19."

## Limitations

- The skill produces an update from the activity it is given. It cannot detect missing items the asker forgot to include — a postponed deliverable that does not appear in the activity will not appear in the update.
- The skill applies a strict health-rating rubric and will sometimes rate a project lower than the asker prefers. If the asker overrides the rating, the skill keeps the override but flags it in `changes_log` so the trail is auditable.
- The skill is opinionated about length. It will not produce a 2,000-word weekly update no matter how much input is supplied; long content goes into `long_version`. If the audience genuinely needs more, that audience needs a different artifact (a quarterly review, a deck, a one-on-one).
- The skill does not handle confidential information specially. If the activity contains items that should not reach the audience, the asker must trim the input.
- Trend display depends on `previous_update`. Without it, the first update is a single point with no comparison. State this in the update so the reader is not misled by an absent trend.
- The skill writes in a neutral, internal-business voice. For a board-level audience that requires more formal cadence, supply a voice constraint in `audience`; the skill will adjust diction but not the underlying structure.

## Sources reviewed

The methodology in this skill was synthesized after reviewing the following permissively-licensed open-source projects. None of their prose, structure, or assets was copied. Each contributed a pattern or a constraint that informed the steps above; the synthesis is original.

- https://github.com/MicrosoftDocs/microsoft-style-guide
- https://github.com/btford/write-good
- https://github.com/amperser/proselint
- https://github.com/openai/openai-cookbook
- https://github.com/othneildrew/Best-README-Template
- https://github.com/elangosundar/awesome-README-templates
- https://github.com/vale-cli/Microsoft
