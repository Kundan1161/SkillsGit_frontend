---
id: skillsgit-curated/pre-deployment-safety-review
version: 1.0.0
name: Pre-Deployment Safety Review Designer
description: Designs the pre-deployment safety review for a robotic system in a new operating context — the test plan, kill-switch verification, observer protocol, escalation rules, and rollback path that gate go-live, formatted for sign-off by a qualified safety engineer.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:functional-safety, pre-deployment, safety-review, kill-switch, observer-protocol, robot-commissioning, rollback]
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
  - pre-deployment review
  - safety acceptance test
  - commissioning safety
  - go-live gate
  - kill-switch test
  - observer protocol
  - robot deployment review
  - safety walkdown
  - safety acceptance criteria
  - new context deployment
example_invocations:
  - "Design the pre-deployment safety review for our AMR going into the new warehouse."
  - "We're moving the welding robot to a new cell; build the go/no-go review."
  - "Help me write the safety acceptance test plan and observer protocol for the cobot."
inputs:
  - name: robot_system_and_change
    type: text
    required: true
    description: The robot system being deployed and the change in operating context — new cell, new facility, new task, new payload, new shift pattern, new operators, or a combination.
  - name: hazards_and_requirements
    type: text
    required: false
    description: The hazard analysis and/or safety requirements available for this deployment. The more material that exists, the sharper the review; without it, the review will be more conservative and will recommend producing the upstream artifacts first.
  - name: site_context
    type: text
    required: false
    description: The physical site — layout, adjacent operations, traffic patterns, who works near the robot, hours of operation, environmental factors.
  - name: existing_safeguards
    type: text
    required: false
    description: Safeguards in place — fences, scanners, light curtains, e-stops, force/torque limits, safety-rated control, safe-state behavior, training program.
  - name: deployment_risk_band
    type: choice
    required: false
    description: A coarse banding of the deployment's risk profile that calibrates the review's depth. Selecting one does not constitute a risk assessment.
    choices: [first-of-kind, change-of-context, repeat-deployment, recovery-after-incident, recovery-after-modification]
outputs:
  - name: pre_deployment_review_plan
    type: markdown
    description: A pre-deployment safety review plan with acceptance criteria, test scenarios, kill-switch verification protocol, observer roles and stations, escalation rules, rollback path, and sign-off gates.
  - name: review_runbook
    type: markdown
    description: A condensed runbook for the day-of review — sequence of actions, who-does-what, the abort-and-rollback procedure, the comms cascade if a test fails, the criteria for proceeding to go-live.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a robotic system is about to be deployed into a new operating context — a new cell, a new facility, a new task, a new payload, new operators, or a combination — and the team needs to design the pre-deployment safety review that will gate go-live. The review is the last opportunity to find what the hazard analysis missed, the safety requirements failed to enforce, or the design assumed away. It is not the safety analysis itself; it is the practical confirmation that the analysis was right and the design is faithful to it. The output is a plan with acceptance criteria, scripted test scenarios, kill-switch verification, observer roles and stations, escalation rules, a rollback path, and explicit sign-off gates that a qualified safety engineer can review, refine, and accept.

Use it when one or more of the following are true: the system has never been operated in this exact context; the system has been modified since the last deployment; the system is returning from an incident or a corrective action; the operators are new to the system; the surrounding work is new or has been reorganized; or the safety engineer wants a structured pre-deployment plan rather than an ad-hoc commissioning. The skill is opinionated about six things. First: **the review is a gate, not a celebration.** Its job is to find reasons not to go live; success looks like discovering an issue at low cost, not validating a decision that has already been made. Second: **the review confirms hypotheses, it does not generate them.** The hazards, the safety requirements, the residual risks — those come from upstream artifacts. The review tests them under conditions representative of the new context. Third: **kill-switches are tested in the configuration they will run in.** A kill-switch verified on a test bench is not verified for production; the switch is tested where the system will operate, by the people who will press it, in the conditions that will be present. Fourth: **observers are named by role and station, with a written brief.** The expectation that anyone present will notice and report is not a protocol; the protocol names who watches what, with what authority, and what they do if they see a deviation. Fifth: **the rollback path is real and rehearsed.** A rollback that exists only on paper is not a rollback; the team practices the path before they commit to the deployment, and the practice is itself a step in the review. Sixth: **the sign-off is by role, not by name, and the gates are sequenced.** The review proceeds through stages, each with a written gate that names what must be true before the next stage begins. Skipping a gate to "save time" is the failure mode the skill is designed to defeat.

Do not use this skill as a substitute for the upstream hazard analysis or safety requirements. The review is downstream of those artifacts; if they do not exist, the skill's first recommendation will be to produce them, not to design a review around their absence. Do not use it as a substitute for qualified safety engineering; the plan is draft input that a safety engineer must accept, refine, and sign.

## Mandatory disclaimer

This skill produces methodology guidance only. Functional safety determinations require qualified safety engineers and, for products entering the market, a notified-body assessment. No skill output may serve as a final hazard analysis, safety case, or certification artifact. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis. The skill produces a review plan; it does not certify a deployment as safe. Acceptance of the deployment is a qualified safety engineer's decision, recorded against the actual evidence produced by the review, in compliance with applicable statutory and standards-based obligations.

## How to apply

The review plan is produced in twelve moves.

1. **Restate the deployment and the change in one paragraph.** What is being deployed, where, into which context, with which task or payload change, with which operators, on which schedule. The paragraph is the plan's grounding context; if the change description is vague, write the paragraph anyway and explicitly mark every guess as an assumption to be confirmed before the review begins. The deployment risk band (first-of-kind, change-of-context, repeat-deployment, recovery-after-incident, recovery-after-modification) is selected and recorded; the band calibrates the depth of the review without substituting for it.

2. **Confirm the upstream artifacts exist and are version-locked.** The review references the hazard analysis (by ID and version) and the safety requirements (by ID and version) that this deployment must satisfy. If either artifact is missing, incomplete, or unversioned, the first recommendation of the plan is to produce the artifact before scheduling the review. The skill does not design a review around a missing analysis.

3. **Define acceptance criteria for go-live.** Acceptance criteria are written before the review. Each criterion ties to a safety requirement or to a residual risk that the safety engineer judged acceptable conditional on a verifying observation. Criteria are binary (yes/no, pass/fail) and time-bounded (the verifying evidence is valid for this deployment, not in perpetuity). Examples: "Safety-rated stop function REQ-FS-001 demonstrated to transition to SS-A within the cycle bound under three triggering modes." "Operator HMI cause-display verified legible from the operator station with normal cell illumination." "Pre-shift verification procedure REQ-Proc-001 executed by the assigned operator with logbook entry." The full set of criteria is the plan's spine; nothing else proceeds without them.

4. **Design the test scenarios that confirm the criteria.** Each criterion gets at least one scenario. Scenarios are scripted: setup, action, observation, pass/fail. Examples: setup — robot in collaborative mode, person-sized obstruction prepared for placement; action — place obstruction within protected envelope while robot is awaiting cycle start; observation — robot does not initiate motion, HMI displays the cause, audit log records the event; pass criterion — all three observed within the cycle bound. Scenarios include normal-condition tests, fault-injection tests, and edge-case tests informed by the loss scenarios in the upstream hazard analysis. Where the loss scenario describes a condition that cannot be safely produced for the review (e.g., a real person stepping into a protected envelope at speed), the scenario uses a representative surrogate (e.g., a calibrated test mannequin or robotic test fixture) and the substitution is recorded.

5. **Verify the kill-switches under representative conditions.** Each kill-switch (hardware e-stop, HMI emergency stop, remote stop, supervisory abort, gateway power-down, network-level cutoff) is tested in the configuration it will run in. The protocol: identify each switch and where it is mounted; verify it is reachable, recognizable, and reachable while wearing the PPE expected in the cell; trigger it from each location; verify the system transitions to its named safe state within the cycle bound; verify the recovery procedure to exit the safe state; verify that activation produces the expected audit-log entry. Kill-switches that fail verification block go-live regardless of other criteria. The verification is repeated after any change to the cell layout or controller configuration.

6. **Design the observer protocol.** Observer roles are named by function: safety engineer (authority to stop), cell operator (executes scripted actions), supervisory engineer (monitors the controller and data), quality observer (records observations in a written log), area safety observer (watches the unfenced or wider area for unplanned ingress). Each observer has a station (a named physical location), a brief (written, one page) describing what they watch, what they record, and what authority they have. Observers are oriented before the review begins; the orientation includes a walk of the cell, a review of the abort criteria, and a confirmation that each observer can communicate with the others.

7. **Specify the abort criteria and the rollback path.** Abort criteria are written before the review and given to all observers: any observer's call to abort is accepted without debate; any test failure that the plan did not anticipate aborts the test in progress; any condition that exposes a hazard not covered by the hazard analysis aborts the entire review pending an upstream update. Rollback is the path back to the prior known-safe state — robot in safe state, cell unpowered if applicable, operators clear, the prior production configuration restored, the cause logged for follow-up. Rollback is rehearsed: before the review begins, the team executes a tabletop rollback (or a live rollback if practical) and confirms each step works.

8. **Design the escalation cascade.** When a test fails, when an unanticipated hazard is observed, or when the abort path is invoked, the cascade names who is notified, in what order, with what content, and by what channel. Examples: cell operator notifies safety engineer immediately by voice; safety engineer notifies the production manager within 15 minutes by phone; safety engineer notifies the integrator's safety lead by email with the observation and the abort decision; if the failure is suspected to indicate a hazard not in the analysis, the integrator's notified-body contact is informed within one business day. Each entry has a fallback if the primary is unreachable.

9. **Stage the review into sequenced gates.** Stage 1: paper review and tabletop — the plan, the upstream artifacts, and the abort criteria are reviewed at a table; the safety engineer signs the gate or returns the plan for revision. Stage 2: powered cell, robot in safe state — kill-switches verified, observer brief executed, comms tested, rollback tabletop completed. Stage 3: controlled scenarios with no payload and no human in the swept volume — functional and monitoring requirements demonstrated. Stage 4: controlled scenarios with representative payload — performance and fail-safe requirements demonstrated, with the area safety observer enforcing the no-person condition. Stage 5: representative operator interactions with the system in the collaborative configuration — the cell operates as it will in production, observed for one or more cycles. Stage 6: go/no-go gate — sign-off by the safety engineer recording the evidence and the residual conditions of acceptance. Each stage's gate is binary, named, and recorded.

10. **Define what proceeds after sign-off, and what does not.** Sign-off is for the deployment as reviewed, in the operating context as reviewed, with the personnel as trained. Changes to the cell layout, the payload, the task, the operators, or the surrounding work invalidate the sign-off and require re-review. The plan names the change-control hooks that trigger re-review and the lightweight re-review path for minor changes (operator turnover within trained crew, payload variation within the validated envelope) versus the full re-review path for significant changes.

11. **Plan the post-deployment observation window.** Going live is not the end of the review. The plan defines a post-deployment window (e.g., the first shift, the first day, the first week, the first 100 cycles) during which the area safety observer remains present, the audit log is reviewed daily, and any deviation from expected behavior triggers a structured pause-and-assess. The criteria for closing the post-deployment window are written; they are evidence-based (no deviations in N consecutive cycles, no operator-reported events, no near-misses) rather than time-based alone.

12. **Compose the plan and the day-of runbook.** The plan is the full document below. The runbook is a condensed companion that fits on a clipboard — sequence of actions, who-does-what, the abort-and-rollback procedure, the comms cascade, the criteria for proceeding to go-live. The runbook is what the cell operator and safety engineer actually carry. The mandatory disclaimer travels in both documents, at the head and the foot.

### Standard pre-deployment safety review plan layout

1. `# Pre-Deployment Safety Review: <system, context>` — version, date, deployment risk band, mandatory disclaimer.
2. `## Deployment and change` — the one-paragraph context and the change being introduced.
3. `## Upstream artifacts` — hazard analysis ID and version, safety requirements ID and version.
4. `## Acceptance criteria` — binary, time-bounded, traced to safety requirements or accepted residuals.
5. `## Test scenarios` — by criterion, scripted with setup/action/observation/pass-fail.
6. `## Kill-switch verification` — switches enumerated, mount locations, verification protocol.
7. `## Observer protocol` — roles, stations, briefs, comms.
8. `## Abort criteria and rollback path` — explicit, including the tabletop or live rehearsal.
9. `## Escalation cascade` — who is notified, in what order, by what channel.
10. `## Staged gates` — Stage 1 through Stage 6, each with a binary sign-off.
11. `## Post-sign-off scope` — what the sign-off covers and the change-control hooks.
12. `## Post-deployment observation window` — duration criteria and the close-out evidence.
13. `## Day-of runbook` — condensed companion for the clipboard.
14. `## Mandatory disclaimer` — repeated in full at the foot.

### Composition rules

- **The review is a gate.** Plans that read as commissioning theatre — full of checklists with no failure paths — are rewritten until they have explicit gates and binary outcomes.
- **Acceptance criteria are written before the test scenarios.** Criteria-first prevents writing scenarios that confirm what the team wanted to confirm anyway.
- **Kill-switches are tested in the production configuration.** Bench tests do not count.
- **Observers have authority, not just attendance.** Each observer can abort.
- **Rollback is rehearsed.** Tabletop is the minimum; live rehearsal is preferred where practical.
- **Sign-off is by role and is recorded against evidence.** Implicit "things looked fine" sign-off is not sign-off.
- **The post-deployment window is part of the plan.** Going live is a stage, not the end.
- **Mandatory disclaimer travels in both documents.**

## Inputs

- **Robot system and change (required, text).** The system and what is changing.
- **Hazards and requirements (optional, text).** Upstream artifacts to anchor the review.
- **Site context (optional, text).** Layout, adjacent operations, traffic, hours.
- **Existing safeguards (optional, text).** What is in place.
- **Deployment risk band (optional, choice).** First-of-kind, change-of-context, repeat-deployment, recovery-after-incident, recovery-after-modification.

## Outputs

A pre-deployment safety review plan and a day-of runbook. Both are draft input to a qualified safety engineer's acceptance and sign-off.

## Examples

### Worked example: AMR moving to a new warehouse floor

**Robot system and change:** "Autonomous mobile robot (AMR) fleet of four, deployed for material handling on a new warehouse floor. The robots were operated in our prior facility under ISO 3691-4. New floor has higher pedestrian traffic, a different aisle layout, three intersection points with pedestrian walkways, and one shared dock area. New operators on the receiving side; existing operators on the shipping side."

**Hazards and requirements:** "Hazard analysis HA-AMR-v2.1 covers the platform; the new-floor delta is captured in HA-AMR-v2.1-delta-newfloor (draft). Safety requirements SR-AMR-v2.1 plus the delta's REQ-F-201 through REQ-F-215 covering the new intersection and dock scenarios."

**Site context:** "Indoor warehouse, mixed lighting (industrial high-bay with skylights producing variable conditions). Aisle layout per drawing W-FLOOR-01. Pedestrian walkways painted; three crossings. Shared dock area with manual forklift traffic during truck-receiving hours (typically 0600-1000 and 1400-1700)."

**Existing safeguards:** "AMR safety-rated lidar with safety-rated speed-and-separation. Audible motion warning. Pre-installed loop antennas at the intersection points for cross-traffic detection. Fleet management system supervises AMR routes; manual forklift activity is reported by the dock supervisor via a status board, not automatically."

**Deployment risk band:** change-of-context

**Expected output (excerpted):**

> # Pre-Deployment Safety Review: AMR Fleet, New Warehouse Floor
>
> Version 0.1 (draft) — deployment risk band: change-of-context.
>
> ## Mandatory disclaimer
>
> This skill produces methodology guidance only. Functional safety determinations require qualified safety engineers and, for products entering the market, a notified-body assessment. No skill output may serve as a final hazard analysis, safety case, or certification artifact. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis.
>
> ## Deployment and change
>
> Four AMRs previously operated on our prior facility floor are moving to the new warehouse floor. The platform is unchanged; the operating context — aisle layout, pedestrian density, intersection geometry, dock sharing with manual forklift traffic — is materially different. The risk band is change-of-context; this review is calibrated for that band.
>
> ## Upstream artifacts
>
> - Hazard analysis: HA-AMR-v2.1 (platform) + HA-AMR-v2.1-delta-newfloor (draft, dated [date], qualified safety engineer: [role]).
> - Safety requirements: SR-AMR-v2.1 + delta REQ-F-201..215.
> - **Pre-review action required:** the delta hazard analysis is in draft. Stage 1 (paper review) does not begin until the delta is signed by the qualified safety engineer.
>
> ## Acceptance criteria (excerpted)
>
> - **AC1.** REQ-F-201 (intersection-priority arbitration) demonstrated to halt the AMR at the intersection-detection line for each of the three intersections, under cross-traffic and no-cross-traffic conditions.
> - **AC2.** REQ-F-205 (dock-area mode) demonstrated to reduce AMR speed to dock-mode limit during dock hours; mode-transition confirmed via fleet manager and audible warning verified.
> - **AC3.** REQ-FS-202 (loss-of-localization safe state) demonstrated by inducing localization degradation in a controlled section; AMR transitions to safe state within cycle bound.
> - **AC4.** Pedestrian-crossing observer protocol demonstrated at each of the three crossings, with the area safety observer confirming the no-pedestrian condition during each scripted test.
> - **AC5.** Kill-switch verification on each AMR (fleet-manager emergency stop, on-AMR e-stop, dock-area cord pull) demonstrated to transition the AMR to safe state within the cycle bound.
> - **AC6.** Pre-shift verification procedure REQ-Proc-201 executed by the assigned dock-side operator with logbook entry; the new operators on the receiving side have completed REQ-T-201 training (records inspected).
>
> ## Test scenarios (excerpted for AC1)
>
> - **Scenario 1.1.** Setup: AMR approaches intersection I-1 with no cross-traffic. Action: AMR proceeds. Observation: AMR slows to the intersection-mode speed limit and confirms no cross-traffic via lidar and the loop antenna signal before proceeding; audit log records the intersection event. Pass: speed reduction observed; audit log present. Fail: speed not reduced, or audit log absent, or cross-traffic signal not consumed.
> - **Scenario 1.2.** Setup: AMR approaches intersection I-1 with a representative pedestrian surrogate placed at the intersection. Action: AMR proceeds. Observation: AMR halts at the intersection-detection line; HMI/fleet-manager records the cause; AMR holds until the surrogate is cleared and the cycle resumes. Pass: AMR halts, cause recorded, resumes only on clear. Fail: any other outcome.
> - **Scenario 1.3.** Setup: AMR at intersection I-2; cross-AMR present from the perpendicular aisle. Action: both AMRs proceed. Observation: arbitration via fleet manager assigns priority; non-priority AMR halts. Pass: arbitration observed and consistent with the rule in REQ-F-201.
>
> ## Kill-switch verification (excerpted)
>
> | Switch | Mount | Verification protocol |
> | --- | --- | --- |
> | On-AMR e-stop (red button, top of platform) | Each of 4 AMRs | Verify reachability while wearing standard warehouse PPE; trigger from approach side; AMR transitions to safe state within cycle bound; audit log entry; recovery procedure exercised. |
> | Fleet-manager fleet-wide emergency stop (workstation) | Fleet manager console | Trigger; all four AMRs transition to safe state within cycle bound; per-AMR audit log entries; recovery requires per-AMR confirmation. |
> | Dock-area cord pull (mechanical, length of dock zone) | Dock area | Walk the length; verify cord triggers from any point; AMRs in the dock zone transition to safe state; AMRs outside the dock zone are not affected. |
> | Intersection emergency lights | I-1, I-2, I-3 | Activate; AMRs approaching the intersection halt; fleet manager records cause. |
>
> Kill-switch verification is the precondition for Stage 3. Failures block go-live regardless of other criteria.
>
> ## Observer protocol (excerpted)
>
> - **Safety engineer (lead, authority to stop).** Stationed at the fleet-manager workstation with view of the floor map and the audit log; signs each stage gate; can abort at any time.
> - **Cell operator (executes scripted actions).** Stationed at the start point of each scenario; carries the runbook; reads the action aloud before performing it.
> - **Supervisory engineer (data and controller).** Stationed at the fleet-manager workstation; records the fleet-manager events and confirms audit-log entries.
> - **Area safety observer A (intersections).** Stationed at each intersection in turn; enforces the no-pedestrian condition during scripted tests; communicates clear status by radio to the safety engineer.
> - **Area safety observer B (dock zone).** Stationed at the dock entry; coordinates with the dock supervisor to pause manual forklift activity during dock-mode scenarios; calls clear when forklift movement is paused and dock zone is verified.
> - **Quality observer (written log).** Records each observation in the review log with timestamp; flags any deviation from the scripted observation.
>
> ## Abort criteria and rollback path
>
> - **Abort criteria.** Any observer's call to abort is accepted without debate. Any test failure that the plan did not anticipate aborts the test in progress. Any condition that exposes a hazard not covered by the hazard analysis aborts the review pending an update.
> - **Rollback path.** All AMRs commanded to safe state via the fleet-manager fleet-wide e-stop. Confirm all four AMRs in safe state via audit log. Confirm pedestrian observers' clear status. Restore the prior production configuration (AMRs reassigned to their prior facility role, if not yet decommissioned, or remain in safe state pending review). Log the cause and the artifacts that need update.
> - **Rollback rehearsal.** Tabletop rehearsal at the start of Stage 1; live rehearsal of fleet-wide e-stop and recovery at the start of Stage 2 before any scripted scenario runs.
>
> ## Escalation cascade
>
> - On any abort: safety engineer notifies the warehouse operations manager by voice within 5 minutes.
> - Safety engineer notifies the integrator's safety lead by email within 30 minutes with the observation and the abort decision.
> - If the failure suggests a hazard not in HA-AMR-v2.1 or the delta: safety engineer notifies the integrator's notified-body contact within one business day.
> - Fallback: if the warehouse operations manager is unreachable, the duty supervisor; if the integrator's safety lead is unreachable, the integrator's on-call line.
>
> ## Staged gates (excerpted)
>
> - **Stage 1: paper and tabletop.** Plan, upstream artifacts (including signed delta hazard analysis), abort criteria reviewed; rollback tabletop completed; safety engineer signs the Stage 1 gate.
> - **Stage 2: powered cell, AMRs in safe state.** Kill-switch verification completed; observer briefs executed; comms tested; rollback live rehearsal completed; safety engineer signs Stage 2.
> - **Stage 3: scripted scenarios without representative payload and without pedestrians in test envelopes.** AC1, AC3 demonstrated; safety engineer signs Stage 3.
> - **Stage 4: scripted scenarios with representative payload, surrogates for pedestrians.** AC1 scenarios with surrogate; AC4 surrogate runs; safety engineer signs Stage 4.
> - **Stage 5: representative operations with trained operators.** AC2 dock-mode runs during actual dock hours with the dock supervisor coordinating manual forklift activity; AC6 records inspected; safety engineer signs Stage 5.
> - **Stage 6: go/no-go.** Safety engineer records evidence, residual conditions of acceptance (if any), and signs go-live or returns the deployment for remediation.
>
> ## Post-sign-off scope
>
> The sign-off covers the AMR fleet operating on the new warehouse floor in the configuration and operator population reviewed. Re-review triggers: change to the AMR platform (firmware, sensors, configuration); change to the aisle layout, intersection geometry, or dock arrangement; addition of a fifth AMR or change in fleet size; change in the operator population beyond the trained crew. Lightweight re-review for: payload variation within validated envelope, operator turnover within trained crew (records inspected, no scenario re-run required).
>
> ## Post-deployment observation window
>
> - Duration: first 7 calendar days of operation OR first 500 cycles per AMR, whichever is longer; close-out requires both windows to be met.
> - Daily audit-log review by the supervisory engineer; flagged events reviewed by the safety engineer within one business day.
> - Area safety observer B remains present during all dock hours for the first 3 days; area safety observer A walks each intersection at least twice per shift for the first 7 days.
> - Close-out: no deviations from the safety requirements observed in the window; no operator-reported safety events; no near-misses logged; close-out signed by the safety engineer and the warehouse operations manager.
>
> ## Day-of runbook (excerpted)
>
> 1. Brief all observers at the floor entrance; confirm comms.
> 2. Execute Stage 2 kill-switch verification per the protocol; record outcomes in the review log.
> 3. Execute rollback live rehearsal; record outcome.
> 4. Execute scenarios 1.1, 1.2, 1.3 in sequence; record observations after each.
> 5. After each scenario, safety engineer asks the quality observer to read back the recorded observation before proceeding to the next scenario.
> 6. If any observation deviates from the pass criterion: abort the test in progress; execute the rollback; convene at the fleet-manager workstation; safety engineer decides whether to remediate and retry or to escalate.
> 7. Proceed through Stages 3, 4, 5 in order; each stage's gate is signed before the next begins.
> 8. Stage 6 go/no-go is recorded with the evidence and the residual conditions of acceptance.
> 9. Post-sign-off: observers transition to the post-deployment-window roles.
>
> ## Mandatory disclaimer
>
> This skill produces methodology guidance only. Functional safety determinations require qualified safety engineers and, for products entering the market, a notified-body assessment. No skill output may serve as a final hazard analysis, safety case, or certification artifact. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis.

## Limitations

- The skill produces a plan, not a sign-off. The qualified safety engineer is the authority who accepts the plan, supervises the review, and signs each stage gate.
- The acceptance criteria are only as good as the upstream artifacts. If the hazard analysis or safety requirements are vague, the criteria will be vague; the skill will note this and recommend that the upstream artifacts be tightened before the review proceeds.
- Surrogates and representative test conditions are imperfect. A mannequin is not a person; a scripted approach is not an operator under production pressure; a controlled cross-traffic event is not the chaos of a busy dock. The plan names the surrogate and the substitution; the residual gap is a matter for the safety engineer's judgment and the post-deployment observation window.
- Kill-switch verification covers the switches as they exist. A switch added after the review is not covered; a switch's mounting changed after the review is not covered; a switch's wiring touched in maintenance is not covered. Change control on kill-switches is the deployment's defense and is named explicitly in the post-sign-off scope.
- Observer authority is exercised by humans under social pressure. An observer who is hesitant to call abort because of cost or schedule pressure is the failure mode the plan names and the safety engineer must defend against. The plan's tone, the orientation, and the visible sign-off discipline are levers; they are not guarantees.
- Post-deployment observation is a window, not a permanent state. The criteria for closing the window are evidence-based, but no window is long enough to surface every latent issue. Ongoing monitoring, incident response, and periodic re-review are separate disciplines.
- Cybersecurity-driven incidents that produce safety consequences (e.g., a compromised controller, a manipulated fleet command) are not within the scope of this review. A parallel cybersecurity assessment is required; integration of the two reviews is a qualified-engineer activity.
- Human-factors realism is partial. Operators under production conditions behave differently from operators in a review. The post-deployment window is partly designed to surface this gap; it does not eliminate it.

## Sources reviewed

- https://github.com/voyage/open-autonomous-safety
- https://github.com/github/codeql-coding-standards
- https://github.com/PagerDuty/incident-response-docs
- https://github.com/counteractive/incident-response-plan-template
- https://github.com/aws-samples/aws-incident-response-playbooks
- https://github.com/vintasoftware/production-launch-checklist
