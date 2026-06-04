---
id: skillsgit-curated/okr-set-reviewer
version: 1.0.0
name: OKR Set Reviewer
description: Critique a set of proposed objectives and key results against best practice — outcome-not-output, measurable, ambitious-but-stretchy, time-bound, cascade-aligned — and produce a revised set with the changes explained.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [niche:product-management, okr, goal-setting, planning, objectives, key-results, leadership]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o]
  tools_required: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 4000
trigger_keywords:
  - review OKRs
  - critique OKRs
  - objectives and key results
  - OKR feedback
  - improve OKRs
  - goal review
  - planning review
  - rewrite OKRs
  - OKR check
  - measurable goals
example_invocations:
  - "Here are our team's Q3 OKRs. Critique them and propose a tighter set."
  - "These OKRs feel like a to-do list. Help me make them outcome-based."
  - "Review the proposed company OKRs and tell me which key results are not measurable."
  - "Check our team OKRs against the company OKRs — is the cascade alignment real?"
inputs:
  - name: okrs
    type: text
    required: true
    description: The proposed OKR set. Free-form is fine; bullet lists with O/KR structure are easiest. Include any units, dates, baselines, and confidence comments the team has written.
  - name: level
    type: choice
    required: false
    description: The level at which these OKRs sit. Affects review criteria. Defaults to team.
    choices: [company, business-unit, team, individual]
  - name: time_horizon
    type: choice
    required: false
    description: The cycle these OKRs cover. Defaults to quarter.
    choices: [annual, half, quarter, month]
  - name: parent_okrs
    type: text
    required: false
    description: The OKRs at the level above (e.g., company OKRs for a team review). Used to check cascade alignment. Without this, alignment is reviewed against the asker's stated company goal in `context`.
  - name: context
    type: text
    required: false
    description: Anything that helps the review — team stage, prior period performance, known constraints, the strategic theme this cycle is supposed to advance, the company goal or vision statement.
outputs:
  - name: critique
    type: markdown
    description: A structured review per objective and per key result with specific issues called out and improvement directions.
  - name: revised_okrs
    type: markdown
    description: A revised OKR set that addresses the critique, with each change traceable to a specific point in the critique.
  - name: meeting_prep
    type: markdown
    description: A short companion artifact for the planning meeting — the three biggest discussion points, the team conversations the revision will provoke, and the suggested order to discuss them.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# OKR Set Reviewer

## When to use

Use this skill when a team has a *draft* of objectives and key results that they want to harden before the planning ritual locks the set for the cycle. The output is a critique of what is there and a revised set the team can take into the room.

Engage when the asker can share at least one objective and the key results that go with it, plus a sentence or two of context. The skill is designed to push back; if the inputs are good, the critique will be short and the revision light. If the inputs are weak, the critique will be specific and the revision substantial.

Decline or push back when:

- The asker wants OKRs *written from scratch* with no goal in mind. Goal-setting starts from strategy and discovery, not from a template. Recommend the prioritization or strategy skill first.
- The asker is using the word "OKR" but actually wants KPIs, project plans, or a backlog. OKRs are *change* commitments, not steady-state metrics. Surface the mismatch and propose the right artifact.
- The asker is in a culture where OKRs are used punitively (missing one ends a job). Ambition and honest measurement do not survive that environment; the critique should warn the asker that no framework choice will fix the underlying problem.
- The OKRs are already locked. If they are this cycle's commitment and the team is mid-cycle, retroactive critique helps the next round; mark the review as forward-looking and frame it as input to the next planning ritual.

The skill is opinionated. The opinions come from the patterns most repeated across the open-source OKR resources surveyed: outcomes beat outputs, key results without units are wishes, ambition without measurability is showmanship, and cascade alignment is real only when each child KR moves at least one parent KR.

## How to apply

Run the methodology in six phases.

### Phase 1 — Parse the proposed OKRs cleanly

1. **Identify each objective and its key results.** Number them: O1 with KR1.1, KR1.2, etc. If the source mixes objectives and key results in a flat list, do the parsing yourself and note the ambiguity.
2. **Count.** A healthy set at the team level for a quarter is 2–4 objectives with 3–5 key results each. More than 5 objectives or more than 5 KRs per objective is a strong signal of dilution. Flag immediately.
3. **Classify each objective.** Three buckets: *aspirational* (a meaningful change in customer or business state), *committed* (a baseline of operations or compliance the team must meet), *learning* (an investigation whose outcome shapes the next cycle). All three are legitimate but the KR criteria differ; an aspirational objective wants stretchy KRs, a committed objective wants binary or threshold KRs.
4. **Classify each key result.** Two buckets: *outcome* (a measurable change in a thing customers or the business cares about) or *output* (a deliverable, a launch, a count of activities). Outputs are not key results in the canonical sense, but teams ship them as KRs anyway. Flag every output and propose an outcome version.

### Phase 2 — Score each objective against the criteria

5. **Outcome, not output.** The objective should describe a *state* the team is trying to achieve, not a *thing* the team is going to build. "Improve activation experience for trial users" is a state; "Ship onboarding redesign" is a build. Flag and rewrite.
6. **Memorable.** A good objective is a phrase a team member can remember without looking it up. If the objective has more than ~15 words or uses jargon stacks, propose a tightening.
7. **Inspiring without being grandiose.** "Become the best in the industry" is grandiose; "Make trial users feel productive within their first session" is inspiring and concrete. Calibrate.
8. **Time-bound.** Either by virtue of the cycle (a quarter implies "by end of Q3") or explicitly inside the objective. Quarterly OKRs do not need a date inside the objective; annual ones often benefit from a milestone.
9. **Aligned with the level above.** Check `parent_okrs` if supplied. Each child objective should advance at least one parent objective, traceably. If the alignment is "we contribute to all parent objectives," the alignment is fake; ask for the specific parent each child supports.

### Phase 3 — Score each key result against the criteria

10. **Measurable.** A KR must have a unit, a baseline, and a target. "Improve retention" is not a KR; "Increase 30-day retention from 42% to 55%" is. If any of unit / baseline / target is missing, flag and propose a complete version.
11. **Outcome, not output.** "Ship the new onboarding flow" is an output; "Increase trial-to-paid conversion from X% to Y%" is an outcome. Outputs masquerading as KRs are the most common defect in the wild; rewrite every one.
12. **Stretchy but not impossible.** The canonical guidance is to set targets such that hitting 70% is a good outcome and 100% is exceptional. Without baseline data, calibrate cautiously. With prior-period performance in `context`, sanity-check the ambition; a target that is 2× prior performance with no plan to invest 2× is fantasy.
13. **Independent of how.** A KR names the change, not the activity. "Run 4 user interviews" is an activity; "Identify the top 2 unmet user needs for trial accounts" is an outcome. Move activities into the team's project plan, not the KR list.
14. **Few enough to focus.** 3–5 KRs per objective. More than 5 means the team is hedging or has not decided what matters. Propose a trim.
15. **Not duplicated across objectives.** If the same KR appears under two objectives, the objectives are not independent. Either merge them or split the KR.
16. **Counter-balanced.** A KR like "Reduce time-to-first-response to 2 hours" without a quality counterweight (CSAT, resolution rate) invites Goodhart's law — the team will hit the speed metric by hurting quality. Recommend a paired guardrail KR where the metric is gameable.
17. **Owner-clear.** Each KR should have an implicit owner (the team or function whose work moves it). If a KR depends on a team that is not in the room, flag the dependency.

### Phase 4 — Score the *set* as a whole

18. **Cohesion.** Do the objectives tell a coherent story for the cycle, or is each one in its own world? A team with 4 unrelated objectives has 4 small teams masquerading as one; flag for a strategy conversation.
19. **Balance.** Does the set cover the team's mandate? A product team's OKRs that have zero KRs about customer outcomes are warning sign. A platform team with zero KRs about reliability or developer velocity is similar. Name the gap.
20. **Capacity.** A set whose KRs together imply more effort than the team has is destined to under-deliver. If the asker has not capacity-checked, flag and recommend a quick exercise (estimate the projects required to move each KR; compare to known team capacity).
21. **Cascade alignment health.** If `parent_okrs` is supplied, verify each child OKR makes at least one parent KR move. If a child KR cannot be traced to a parent KR, either the cascade is wrong or the OKR does not belong in this set.
22. **Stretch calibration.** Across the set, if every KR is wildly ambitious, the team will demoralize; if every KR is sandbagged, the cycle is wasted. Look for a mix; recalibrate where uniformly off in either direction.
23. **The "not-OKR" check.** Some critical work is not OKR-shaped — keeping the lights on, paying down a specific known debt, complying with a regulation. Note any work the asker mentioned in `context` that does not appear in the OKRs *and does not need to* — explicitly carve it out as committed work tracked outside the OKR system. This prevents teams from cramming maintenance into objectives.

### Phase 5 — Produce the revised set

24. **Rewrite, do not annotate-and-leave.** The asker will copy the revised set into their planning doc. The revision must be usable as-is.
25. **Preserve the team's voice.** Keep wording the team used where it is good. Do not impose a generic corporate cadence on a team that writes plainly. Calibration, not replacement.
26. **Show the diff in the critique, not the revised set.** The revised set reads cleanly; the critique tells the reader what changed and why. Two artifacts, two purposes.
27. **Bound the count.** If the proposed set had 6 objectives, the revised set should have 2–4 unless the asker has explicitly justified the extras. Be willing to consolidate; an objective that absorbs two weaker ones is often stronger than either.
28. **Add a "tracking note" per KR.** A single sentence: how this KR will be measured (which dashboard, which query, which survey, which manual count). KRs that cannot be tracked are KRs that will not be tracked.
29. **Where ambition is unclear, propose a range.** "Increase trial-to-paid conversion from 12% to 18–22% (commit 18, stretch 22)." Lets the team commit and dream in the same artifact.

### Phase 6 — Compose the meeting-prep companion

30. **Identify the three biggest discussion points.** Not the smallest fixes; the conversations the team needs to have. Examples: "Is the activation objective the right top priority for this team, given the parallel work on enterprise rollout?" "Are we okay with a stretchy 22% target if the engineering team has not committed effort yet?" "Should the dependency on the data team be flagged as a parent-level issue?"
31. **Order them by what unblocks others.** Strategic discussions first, calibration discussions second, wording fixes last. Teams that argue wording for 40 minutes will not get to the strategic point.
32. **Note the silences.** What is *not* in the OKRs that probably should be? A team without any customer-outcome KR is silent on customers. Name the silence.
33. **Confidence-tag the review.** "High confidence — parent OKRs supplied, prior-period data available." "Medium — no parent OKRs; alignment reviewed against stated company goal only." "Low — sparse context, no metrics; review is mostly form, not strategy."

## Inputs

- **`okrs`** — required. The draft set. Bullet structure with O/KR labels is easiest, but free-form is handled.
- **`level`** — optional. `company`, `business-unit`, `team`, `individual`. Defaults to `team`.
- **`time_horizon`** — optional. `annual`, `half`, `quarter`, `month`. Defaults to `quarter`. Affects ambition and time-bound checks.
- **`parent_okrs`** — optional. The level above. Without it, cascade is reviewed only against the asker's stated company goal in `context`.
- **`context`** — optional. Team stage, prior-period performance, strategic theme, known dependencies. Lifts the review from form to substance.

## Outputs

- **`critique`** — issue-by-issue feedback with directions to improve.
- **`revised_okrs`** — a usable revised set.
- **`meeting_prep`** — the three discussion points and the suggested order.

## Examples

### Example 1 — A draft set that reads like a to-do list

**Source.** A team submits three objectives. KRs include "Ship the onboarding redesign," "Launch the new pricing page," "Run 8 user research interviews," "Write the Q4 strategy doc."

**Output highlights.**

- **Critique.** Every KR is an output. The set is a project plan, not OKRs. Objective wording focuses on activities ("Improve onboarding") not states ("New trial users feel productive in their first session").
- **Revised set.** 2 objectives instead of 3 (the strategy doc gets carved out as committed work tracked separately). Each KR rewritten as an outcome: "Increase first-week activation rate from 38% to 50%" replaces "Ship the onboarding redesign," with a tracking note: "measured weekly on the activation dashboard." The user-research KR becomes "Identify and validate the top 2 unmet needs for trial accounts week-2 through week-4 (validated via 2 evidence sources per need)."
- **Meeting prep.** Top discussion point: "Are we comfortable committing to 50% activation when the redesign work has not been scoped yet? Recommend committing to a range (45–50%) and stretch-checking after week 4 of engineering scoping."

### Example 2 — Cascade alignment broken between team and company

**Source.** Company OKRs in `parent_okrs` focused on enterprise expansion. Team OKRs are entirely about self-serve activation. Context: the team is the self-serve team.

**Output highlights.**

- **Critique.** Cascade alignment is weak by design — the team is misnamed in the cascade. The team's OKRs are good for *what they are*, but the parent set does not have a self-serve objective for them to attach to. Two paths: lobby for a self-serve parent objective, or reframe team objectives to show how self-serve quality drives enterprise interest.
- **Revised set.** Two versions: a defensible self-serve version with a written rationale ("Self-serve quality is a leading indicator of enterprise pipeline because X") and an alternative where one objective is reframed to show enterprise contribution. Asker chooses.
- **Meeting prep.** Surface the cascade gap to leadership as a structural issue, not a team issue.

### Example 3 — Over-ambitious set with no capacity check

**Source.** A 4-person team with 5 objectives, 6 KRs each, all stretch.

**Output highlights.**

- **Critique.** Count exceeds healthy capacity by ~3x. Even at 70% target attainment, the implied effort is double the team's quarterly capacity.
- **Revised set.** 3 objectives, 4 KRs each. Two objectives merged. Stretch calibration recommended: commit at 70% of original stretch targets, stretch at original. Tracking notes for each.
- **Meeting prep.** Top discussion: "Which 5 of the original 30 KRs are non-negotiable for this cycle? Bring it to the room as a forcing function before the merge is finalized."

## Limitations

- The skill cannot judge whether the team is working on the right things. It judges the quality of how the OKRs are *expressed*. A perfectly-written OKR about the wrong problem is still the wrong problem.
- Without `parent_okrs`, cascade alignment is partial. The skill flags this clearly in the confidence note.
- Stretch calibration without baseline data is opinion. The skill flags every ambition claim that is not supported by prior performance.
- Some company cultures have OKR conventions the skill will violate (e.g., always 3 objectives, always all-outputs because that's how the company runs). The skill will note the divergence and let the asker decide.
- The skill does not lobby. If the cascade is broken or the level above has set bad parent OKRs, the skill names the issue and suggests how to raise it, but cannot raise it for the asker.
- The skill produces a draft, not a commitment. Final OKR adoption is a human ritual; the artifact informs the conversation.

## Sources reviewed

The methodology in this skill was synthesized after reviewing the following permissively-licensed open-source projects. None of their prose, structure, or code was copied. Each contributed a pattern or a constraint that informed the steps above; the synthesis is original.

- https://github.com/phuryn/pm-skills
- https://github.com/product-on-purpose/pm-skills
- https://github.com/ploi/roadmap
- https://github.com/github/spec-kit
- https://github.com/anombyte93/prd-taskmaster
