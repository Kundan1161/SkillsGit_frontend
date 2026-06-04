---
id: skillsgit-curated/robot-hazard-analysis-conductor
version: 1.0.0
name: Robot Hazard Analysis Conductor
description: Runs a structured hazard analysis on a robotic system — identifies hazards, unsafe control actions, loss scenarios, and the safety constraints that mitigate them, in a HAZOP-plus-STPA-lite synthesis suitable for downstream review by qualified safety engineers.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:functional-safety, hazard-analysis, stpa, hazop, iso-13849, iec-61508, robotics-safety]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 10000
trigger_keywords:
  - robot hazard analysis
  - HAZOP
  - STPA
  - unsafe control action
  - loss scenario
  - safety constraint
  - functional safety
  - robot risk assessment
  - cobot risk
  - ISO 13849
  - IEC 61508
  - ISO 10218
  - R15.06
example_invocations:
  - "Run a hazard analysis on our pick-and-place cobot cell before we hand it to the safety engineer."
  - "I need an STPA-lite of the new AMR — losses, unsafe control actions, and constraints."
  - "Help me draft a hazard analysis for our welding robot integration; we'll get it reviewed by a notified body."
inputs:
  - name: robot_system_description
    type: text
    required: true
    description: Plain-language description of the robot system — what it is, what it does, where it operates, what it interacts with (humans, payloads, other machines, load-bearing structures), and the rough physical envelope.
  - name: operating_context
    type: text
    required: false
    description: Where and how the robot will be used — cell layout, fixed/mobile, presence of operators or bystanders, expected operating hours, environmental factors (lighting, dust, wet, outdoor), known adjacent equipment.
  - name: control_architecture
    type: text
    required: false
    description: How the robot is controlled — autonomous, teleoperated, supervisory, mixed; control loop closure (vision, force, torque); communications topology; safety-rated vs. non-safety-rated controllers.
  - name: existing_safeguards
    type: text
    required: false
    description: Safeguards already designed or in place — fences, light curtains, scanners, e-stops, force/torque limits, speed/separation monitoring, safety-rated control, interlocks.
  - name: applicable_standards
    type: choice
    required: false
    description: The regulatory or normative regime the deployment will need to satisfy, used to bias terminology and downstream artifacts. Selecting one does not constitute a compliance opinion.
    choices: [iso-13849, iec-61508, iso-10218-ansi-r15-06, iso-13482, iso-3691-4-amr, mixed-or-unknown]
outputs:
  - name: hazard_analysis_document
    type: markdown
    description: A structured hazard analysis covering system context, losses, hazards, unsafe control actions, loss scenarios, and a draft set of safety constraints — formatted for downstream review by a qualified safety engineer.
  - name: open_questions_register
    type: markdown
    description: A list of unanswered questions, missing information, and assumptions made by the skill that the human safety team must close before the analysis can be considered complete.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a robot or robotic system is being designed, integrated, or re-deployed and a structured hazard analysis is needed as input to a qualified safety engineering review. The skill produces an analysis with the right shape — system context, losses, hazards, unsafe control actions, loss scenarios, draft safety constraints, and an explicit register of open questions — drawing on the discipline of HAZOP (deviation-driven, guideword-led) and STPA (control-structure-driven, hazard-as-system-state). It is intended for the early stages of a project when the team needs a tractable, traceable starting point that a human safety engineer can refine, contest, and certify.

Use it when one or more of the following are true: the robot will interact with people or load-bearing structures; the integration is new or significantly changed; the team has a working understanding of the system but has not yet written down a hazard analysis; or the team has a draft analysis and wants a second-opinion structural pass before it goes to a notified body or internal safety review board. The skill is opinionated about four things. First: **a hazard is a system state, not a failed component.** A motor that overheats is a failure; a robot end-effector arriving at an unintended location while a person is in the workspace is a hazard. Mistaking failures for hazards produces analyses that miss the failures of correctly-functioning components and the hazards of human-machine interactions. Second: **unsafe control actions are enumerated by structure, not by imagination.** For every control action the system can issue, exactly four questions are asked: providing it when it should not be provided; not providing it when it should be; providing it too early, too late, or in the wrong order; stopping it too soon or applying it too long. This structure beats free-form brainstorming because it forces coverage. Third: **safety constraints are derived from loss scenarios, not from the controls catalog.** The analysis names what the system must not do, and then mitigations are chosen to enforce that. Building a list of mitigations first and then justifying them is how teams ship systems that satisfy nobody. Fourth: **every assumption is logged and every open question is named.** A skill running cold on a written description will inevitably make assumptions about geometry, payload, control authority, and environment. Those assumptions are surfaced explicitly so the human reviewer can confirm or replace them.

Do not use this skill as a standalone certification artifact, a sign-off document, or a substitute for a qualified safety engineer. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis. This skill produces methodology guidance only.

## Mandatory disclaimer

This skill produces methodology guidance only. Functional safety determinations require qualified safety engineers and, for products entering the market, a notified-body assessment. No skill output may serve as a final hazard analysis, safety case, or certification artifact. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis. The skill cannot determine Performance Level (ISO 13849), Safety Integrity Level (IEC 61508/61511), or category ratings; those determinations require a quantitative analysis and a qualified safety engineer with access to component data and the as-built system. Cite this output only as draft input to a human-led review, never as a conclusion.

## How to apply

The analysis is produced in twelve moves. Each move ends with a written section and a contribution to the open-questions register.

1. **Restate the system in one paragraph.** Capture what the robot is, what it does, where it operates, who and what it interacts with, and the rough physical envelope. The paragraph is the analysis's grounding context; if the description in the input is vague, write the paragraph anyway and explicitly mark every guess with `[assumption: ...]`. Each assumption goes to the open-questions register.

2. **Enumerate the system boundary.** Inside the boundary: the robot, its end-effector, its controller, its sensors, its safety-rated subsystem if present, and any tightly-coupled fixed equipment. Outside the boundary: the operator, the bystander, the workpiece, adjacent machines, the building, the network the robot may report to. Things-on-the-boundary: emergency stop devices, fences, light curtains, scanners, HMIs. The boundary determines which losses are in scope and which control actions count.

3. **Name the losses.** A loss is an unacceptable outcome, expressed in terms a non-engineer can understand. Standard losses for a robotic system to seed from: human injury (operator, bystander, maintainer, member of the public); damage to the workpiece, the robot, or adjacent equipment; release of stored energy (pneumatic, hydraulic, electrical, kinetic); release of a substance (coolant, lubricant, process chemical, weld fume); loss of the load (drop, ejection); compromise of a load-bearing structure the robot interacts with; environmental release; data or model corruption that propagates into future control actions. Tailor the list to the system; reject losses that the boundary excludes; flag losses that depend on context that the input did not provide.

4. **Derive the hazards.** A hazard is a system state that, combined with worst-case environmental conditions, leads to a loss. Hazards are written in the form "the system [state] while [context]." Examples seeded for a manipulator: "the end-effector arrives at an unintended pose while a person is within the protected envelope"; "the gripper releases the payload while it is over a person or another machine"; "the robot exerts force in excess of the contact-force limit while contacting a person"; "the safety controller fails to detect intrusion of the protected envelope while the robot is moving at high speed." Each hazard maps to one or more losses from step 3. Hazards are not failures; "the motor overheats" is a failure that may contribute to a hazard but is not the hazard itself.

5. **Identify the control actions.** A control action is something the control system or a human controller can command the robot to do. Standard list to seed: move (with target, velocity, trajectory parameters); open or close end-effector; pick or place payload; engage or release a brake; enter or exit collaborative mode; reset after a stop; resume from a paused state; transition between programs; acknowledge an alarm; report state to a supervisory system. Each control action is the unit of analysis for step 6.

6. **For each control action, enumerate the unsafe control actions (UCAs) by the four-question structure.** (a) **Providing the action when it should not be provided** — e.g., "moving while a human is in the protected envelope," "releasing the gripper while the payload is over a person," "resetting after an emergency stop without confirmation that the cause is cleared." (b) **Not providing the action when it should be provided** — e.g., "failing to issue the brake command when an obstacle is detected at safety distance," "not transitioning to safe state on detected sensor degradation." (c) **Providing the action too early, too late, or in the wrong order** — e.g., "issuing the move command before the workpiece-clamp is confirmed closed," "issuing the gripper-close command after the end-effector has already retracted." (d) **Providing the action for too long or stopping too soon** — e.g., "continuing motion past the planned endpoint due to a latched command," "ending an emergency-stop ramp before the robot is below safe speed." Not every cell of the matrix yields a meaningful UCA; record the cells that do, and record cells that are explicitly inapplicable (rather than silently skipped) so the reviewer can confirm coverage.

7. **For each UCA, build at least one loss scenario.** A loss scenario answers the question: how could the UCA actually occur in the system as designed? Scenarios trace through the control structure: the controller process model is wrong (it believes the cell is clear when it isn't); a sensor degrades silently (the light curtain reports clear because of glare or contamination); the actuator does not respond as commanded (the brake-release valve sticks); an external disturbance (a person enters through an unprotected approach the model did not consider); a coordination failure between two controllers (the cell controller commands move while the safety controller has not yet completed its self-test); a software defect (the speed-and-separation algorithm has an edge case at the workspace boundary). Scenarios are concrete and traceable; "something fails" is not a scenario. Each scenario names the controller, the process variable, and the propagation path from the variable's wrong value to the UCA.

8. **Derive safety constraints from the scenarios.** A safety constraint is a statement of what the system must enforce to prevent the UCA. Constraints are written as imperatives: "the controller shall not issue a move command unless the protected envelope is confirmed clear by two independent sources within the previous 100 ms"; "the safety controller shall transition to safe state if any of the protected-envelope sensors reports degraded for more than one diagnostic cycle"; "no operator-issued reset shall clear an emergency stop until the operator has acknowledged a written check that the cause is removed." Each constraint maps back to one or more scenarios and forward to one or more mitigations to be assigned in step 9. Constraints describe what; mitigations describe how.

9. **Map constraints to mitigation strategies, at the level a safety engineer can refine.** Mitigation strategies are categorized: (i) **inherent safety** (eliminate the hazard by design — reduce mass, reduce reach, reduce stored energy, separate operations in time); (ii) **safety-rated control** (use a safety-rated subsystem appropriate to the standard regime — speed-and-separation monitoring, power-and-force-limiting, safe operating stop, safely-limited speed); (iii) **safeguarding** (light curtains, scanners, fences, interlocks, two-hand controls); (iv) **complementary protective measures** (e-stops, awareness signals, restart enabling devices); (v) **information for use** (markings, signs, manuals, training). The order of preference is the order listed; the analysis names the level at which each constraint is intended to be enforced and flags any constraint that is enforced only by information-for-use as needing the safety engineer's particular attention. The analysis does not assign Performance Level, Safety Integrity Level, or category — those are quantitative determinations that require component data and a qualified engineer.

10. **Surface the residual hazards.** After mitigations are assigned, some loss potential remains. Residual hazards are the ones the design tolerates because the mitigation is judged adequate. Each residual is named, the rationale recorded, and the human reviewer flagged. The point is not to claim the residual is acceptable; the point is to make it visible so the human can decide.

11. **Write the open-questions register.** Every assumption made during steps 1-10, every gap in the input, every place the skill chose between two reasonable interpretations, every place the analysis depends on data the skill does not have. The register has columns: question, why it matters (which constraint, scenario, or mitigation it bears on), who can answer it (role, not name), and whether the analysis can proceed without it. Skill output that does not include a substantial register is a red flag — robotics safety analyses always have open questions on first pass.

12. **Compose the document.** The output uses the standard layout below. Each section cross-references the others by stable IDs (L1, L2 for losses; H1, H2 for hazards; CA1 for control actions; UCA1.a, UCA1.b for unsafe control actions; SC1 for scenarios; C1 for safety constraints; M1 for mitigations; R1 for residuals; Q1 for open questions). The IDs are how the safety engineer reads the document; lazy referencing breaks the chain.

### Standard hazard analysis layout

1. `# Hazard Analysis: <system name>` — version, date, applicable standards regime if specified, the mandatory disclaimer in full.
2. `## System description` — the one-paragraph statement and the system boundary.
3. `## Losses (L#)` — numbered list, each loss in a sentence a non-engineer would understand.
4. `## Hazards (H#)` — numbered table, each hazard as "system state while context," with the losses it maps to.
5. `## Control actions (CA#)` — numbered list of the actions the control system can issue.
6. `## Unsafe control actions (UCA#)` — a sub-table for each CA, with the four-question structure and the hazards each UCA maps to.
7. `## Loss scenarios (SC#)` — for each UCA, one or more scenarios with controller, process variable, and propagation path.
8. `## Safety constraints (C#)` — imperatives traceable from scenarios.
9. `## Mitigation strategies (M#)` — by category, by constraint, flagging information-only mitigations for safety-engineer review.
10. `## Residual hazards (R#)` — visible by design.
11. `## Open questions register (Q#)` — explicit, with who-can-answer.
12. `## Standards alignment note` — a paragraph naming the applicable standards regime selected (if any), and flagging that quantitative determinations (PL, SIL, category) are out of scope for the skill and must be performed by a qualified safety engineer with access to component data.
13. `## Mandatory disclaimer` — repeated in full at the end of the document so it travels with extracts.

### Composition rules

- **Hazards are system states, not component failures.** A failure is a contributing cause; the hazard is the unsafe state.
- **Every UCA links to a hazard; every scenario links to a UCA; every constraint links to a scenario; every mitigation links to a constraint.** Orphaned items are removed or moved to the open-questions register.
- **Assumptions are explicit.** Every `[assumption: ...]` becomes a Q-row.
- **The analysis is conservative on coverage and humble on conclusions.** It is acceptable for a UCA cell to read "no plausible failure mode at this level of analysis, to be confirmed in detailed design." It is not acceptable to omit the cell silently.
- **No PL/SIL/category assignment.** Those are out of scope and named so.
- **Mandatory disclaimer appears at the head and the foot.** Extracts that lose the disclaimer should still carry the warning.

## Inputs

- **Robot system description (required, text).** What the robot is, what it does, where it operates, what it interacts with.
- **Operating context (optional, text).** Cell layout, presence of operators or bystanders, environmental factors.
- **Control architecture (optional, text).** Autonomy level, control loops, safety-rated vs. non-safety-rated subsystems.
- **Existing safeguards (optional, text).** Fences, light curtains, scanners, e-stops, force/torque limits, speed-and-separation.
- **Applicable standards (optional, choice).** ISO 13849, IEC 61508, ISO 10218 / ANSI R15.06, ISO 13482, ISO 3691-4 (AMR), or mixed-or-unknown. Selecting one biases terminology only; it does not constitute a compliance opinion.

## Outputs

A structured hazard analysis document and a companion open-questions register. Both are draft input to a human-led review by a qualified safety engineer.

## Examples

### Worked example: collaborative pick-and-place cell

**Robot system description:** "A 6-axis collaborative robot mounted on a fixed pedestal next to a conveyor. End-effector is a two-finger parallel gripper handling injection-molded plastic parts up to 800 g. The robot picks parts from a conveyor and places them in a tote on the operator side. Operator approaches the cell to swap totes when full. The cell is not fenced; it is laid out as a collaborative workspace."

**Operating context:** "Indoor, factory floor, normal industrial lighting. Operator is on the cell side at a workbench reaching into the tote area approximately once every two minutes. Bystanders (other operators, supervisors) may approach within two meters."

**Control architecture:** "Robot controller is the manufacturer's safety-rated controller with power-and-force-limiting in collaborative mode. Cell PLC supervises the conveyor and tote sensors. Operator HMI on the cell side has a single-button reset. Vision system on the conveyor identifies part position; no person-detection vision is installed."

**Existing safeguards:** "Power-and-force-limiting in collaborative mode (manufacturer-rated). Two-hand reset on the HMI for resuming after a stop. E-stop on the HMI and on a remote pendant. No light curtains, no scanners, no force-torque sensor at the wrist."

**Applicable standards:** iso-10218-ansi-r15-06

**Expected output (excerpted):**

> # Hazard Analysis: Collaborative Pick-and-Place Cell
>
> Version 0.1 (draft) — applicable standards regime: ISO 10218 / ANSI R15.06.
>
> ## Mandatory disclaimer
>
> This skill produces methodology guidance only. Functional safety determinations require qualified safety engineers and, for products entering the market, a notified-body assessment. No skill output may serve as a final hazard analysis, safety case, or certification artifact. Robot deployments that interact with people or load-bearing structures must follow applicable statutory safety regulations regardless of any AI-assisted analysis.
>
> ## System description
>
> A 6-axis collaborative robot on a fixed pedestal performs pick-and-place between a conveyor and a tote. The operator shares the workspace and reaches in to swap totes. Cell is unfenced and relies on the manufacturer's power-and-force-limiting in collaborative mode. Boundary: the robot, controller, gripper, vision system, cell PLC, HMI, e-stops, conveyor, and the tote fixture. Outside the boundary: operator, bystanders, workpiece (in transit), adjacent equipment.
>
> ## Losses
>
> - **L1.** Operator or bystander suffers injury from contact with the robot or its payload.
> - **L2.** Payload is dropped onto operator, bystander, or equipment.
> - **L3.** Operator or bystander is struck by an unexpected motion of the robot during an apparent rest state.
> - **L4.** Workpiece is damaged in a way that propagates to a downstream safety-relevant process (assumption: downstream uses are documented elsewhere; Q3).
>
> ## Hazards
>
> | ID | State while context | Maps to losses |
> | --- | --- | --- |
> | H1 | The robot exerts force on a person in excess of the collaborative-mode contact limit while in motion | L1 |
> | H2 | The gripper releases the payload while the payload is over a person or above the tote rim, releasing kinetic energy onto the person or causing a fall | L2 |
> | H3 | The robot initiates motion while a person's hand or arm is within the protected reach envelope | L1, L3 |
> | H4 | The robot resumes from a stop state while the cause of the stop is unresolved | L1, L3 |
> | H5 | Power-and-force-limiting fails-silent (continues to operate but no longer enforces the limit) while the robot is in collaborative mode | L1 |
> | H6 | The robot reaches outside the planned envelope due to a control or model error while a person is in the adjacent area | L1, L3 |
>
> ## Control actions
>
> - **CA1.** Issue move command (to target pose, with velocity profile)
> - **CA2.** Open gripper
> - **CA3.** Close gripper
> - **CA4.** Engage brake (on detected fault)
> - **CA5.** Transition between collaborative and non-collaborative mode (assumption: non-collaborative mode is not enabled in this cell; Q5)
> - **CA6.** Acknowledge an alarm / reset after stop
> - **CA7.** Report cell state to supervisory PLC
>
> ## Unsafe control actions (excerpted for CA1)
>
> | Cell | UCA | Maps to hazard |
> | --- | --- | --- |
> | CA1.a | Provided when it should not be: move command issued while a person's hand is within the planned trajectory's swept volume | H3, H1 |
> | CA1.b | Not provided when it should be: brake/decelerate command not issued when a sudden change in load detected (interpretable as a person leaning into the path) | H1, H3 |
> | CA1.c | Provided in wrong order: move issued before the tote-swap acknowledgement is confirmed by the operator HMI | H3 |
> | CA1.d | Provided too long: trajectory continues past the planned endpoint due to an extended motion segment ([assumption: motion is bounded by safety-rated soft limits in the controller; Q7]) | H6 |
>
> ## Loss scenarios (excerpted for UCA CA1.a)
>
> - **SC1.** The vision system identifies a part on the conveyor and the cell controller schedules a pick. The cell controller's process model assumes the operator is at the bench (last-known state from a non-safety-rated proximity assumption). The operator has approached the tote and reached in. No person-detection sensor is installed (assumption: confirmed in input). The robot initiates the move. Power-and-force-limiting will reduce the energy of contact but does not prevent the contact. Maps to UCA CA1.a, H3, H1, L1.
> - **SC2.** A bystander walks past the open side of the unfenced cell while the robot is in motion. The bystander's path is incidentally clipped by the robot's swept volume. Same propagation as SC1. Maps to UCA CA1.a, H3, L1.
>
> ## Safety constraints (excerpted)
>
> - **C1.** The controller shall not issue a move command unless the protected reach envelope is confirmed clear of persons by a means independent of the operator's stated location. (Derived from SC1, SC2.)
> - **C2.** The controller's force limit in collaborative mode shall be enforced by a means whose failure is diagnosable within one cycle. (Derived from H5.)
> - **C3.** Any reset after a stop shall require an action by the operator that confirms the cause has been investigated; a single-button reset that does not require this confirmation shall not be present. (Derived from H4; flags the current single-button HMI as a finding.)
> - **C4.** The cell shall provide an awareness barrier (visual, physical, or sensed) that bounds the bystander-relevant envelope. (Derived from SC2.)
>
> ## Mitigation strategies (excerpted)
>
> | Constraint | Strategy level | Notes |
> | --- | --- | --- |
> | C1 | Inherent safety (reduce reach envelope) OR safety-rated control (add a scanner with safety-rated person-detection) OR safeguarding (add a light curtain on the operator side) | Information-for-use alone (a sign telling the operator to keep clear) is insufficient and is flagged for safety-engineer review. |
> | C2 | Safety-rated control (manufacturer's diagnostic coverage of the power-and-force-limiting subsystem) | Requires confirmation from the manufacturer's datasheet and the integrator's assessment. Out of scope of this skill. |
> | C3 | Complementary protective measures (HMI redesign for a two-stage reset with cause-cleared confirmation) | Current HMI is a finding. |
> | C4 | Safeguarding (physical or sensed bystander-area boundary) | Inherent-safety alternative is to relocate the cell so that the unfenced side is not adjacent to a walkway. |
>
> ## Residual hazards
>
> - **R1.** Contact with the operator at the manufacturer-rated power-and-force-limited level may still occur during permitted collaborative operations; the limit reduces but does not eliminate the contact-energy hazard. The acceptability of this residual is a safety-engineer decision informed by ISO/TS 15066-style force-and-pressure analysis, which is out of scope of this skill.
>
> ## Open questions register (excerpted)
>
> | ID | Question | Why it matters | Who can answer |
> | --- | --- | --- | --- |
> | Q1 | Is the power-and-force-limiting subsystem's diagnostic coverage documented and validated by the manufacturer? | C2; H5 | Robot manufacturer + integrator's safety engineer |
> | Q2 | What is the worst-case payload kinetic energy at the worst-case point in the trajectory, given the 800 g part? | H1 force-limit applicability | Integrator's safety engineer + dynamic analysis |
> | Q3 | Does the workpiece feed a downstream safety-relevant process? | L4 in or out of scope | Process engineer |
> | Q4 | What is the geometry of the unfenced sides relative to the walkway? | SC2, C4 | Facility layout |
> | Q5 | Is non-collaborative mode enabled or strictly disabled in this cell? | CA5 scope | Integrator |
> | Q6 | What is the actual approach pattern of the operator — frequency, posture, reach geometry? | SC1, force-limit assumptions | Observation by the safety engineer |
> | Q7 | Are safety-rated soft limits configured for the swept volume, and what is their diagnostic coverage? | CA1.d, H6 | Integrator |
>
> ## Standards alignment note
>
> This analysis is structured for compatibility with ISO 10218 / ANSI R15.06 review of an integrated collaborative robot cell. It does not constitute a compliance opinion. Performance Level (per ISO 13849), SIL (per IEC 61508/61511), and category are not assigned here; those determinations require a quantitative analysis and a qualified safety engineer with access to the as-built component data.

## Limitations

- The skill is methodology guidance only. It cannot assign PL, SIL, or category, and it cannot produce a certification artifact. The mandatory disclaimer is repeated at the head and foot of every output for this reason.
- The analysis is only as good as the input. A vague description of the system produces a vague analysis with a long open-questions register. The register is the honest signal; teams that find the register longer than the analysis should treat that as information rather than a deficiency.
- The skill defaults to a conservative posture. Where two interpretations are plausible, it picks the worse-consequence interpretation and flags the choice in the register. A reviewer who knows the system can argue the choice down.
- Coverage by the four-question UCA structure is structural, not exhaustive. There are hazards that arise from interactions between systems and environments that no four-cell structure surfaces. The standards regime cited (HAZOP, STPA) acknowledges this and prescribes additional techniques (functional decomposition, environmental survey, human-factors review) that this skill does not perform.
- Quantitative analyses are out of scope. The skill does not compute reliability numbers, failure rates, mean times to dangerous failure, or diagnostic coverage. These are required for PL and SIL determinations and must be performed by a qualified engineer with access to component data.
- Human factors are touched but not deeply analyzed. The skill notes operator interactions and the role of awareness, but a serious human-factors review (task analysis, cognitive load, training adequacy) is its own discipline and is not substituted by this skill.
- Cybersecurity is adjacent but out of scope. A controller compromised by a network attack can produce hazards; this skill notes the network-as-boundary item but does not perform a security analysis. A separate review (e.g., IEC 62443-aligned) is required.
- The skill is genuinely cautious about claims of completeness. Robotics safety is a domain where what the analysis missed is what hurts people. The output's tone reflects that.

## Sources reviewed

- https://github.com/voyage/open-autonomous-safety
- https://github.com/github/codeql-coding-standards
- https://github.com/davidski/evaluator
- https://github.com/PagerDuty/incident-response-docs
- https://github.com/counteractive/incident-response-plan-template
- https://github.com/aws-samples/aws-incident-response-playbooks
