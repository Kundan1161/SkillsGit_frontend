---
id: skillsgit-curated/robot-vlm-instruction-grounding-architect
version: 1.0.0
name: Robot VLM Instruction Grounding Architect
description: Design a parse-plan-act-verify loop that grounds natural-language instructions to robot actions using a vision-language model, including refusal patterns, ambiguity resolution, and safety filtering.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:vlm-multimodal-perception, instruction-following, language-grounding, parse-plan-act-verify, ambiguity-resolution, refusal-patterns, safety-filter]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, code_execution, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - robot instruction following
  - natural language to robot actions
  - vlm instruction grounding
  - parse plan act verify
  - language grounded robot
  - refusal patterns robot
  - ambiguity resolution robot
  - referring expression robot
  - vlm safety filter
  - instruction to action
  - language conditioned policy
  - grounded planning robot
example_invocations:
  - "Design the architecture for grounding operator instructions like 'pick up the red mug on the second shelf' into manipulator actions on our research arm."
  - "How should we handle ambiguous referring expressions on our home assistant robot when there are multiple matching objects?"
  - "Architect the safety filtering layer between a frontier VLM and the actual motion executor for our service robot."
inputs:
  - name: platform_description
    type: text
    required: true
    description: Robot, its action space, the perception capabilities already available, and the operator's typical instruction style.
  - name: instruction_domain
    type: text
    required: false
    description: The kinds of instructions the platform must support — navigation, manipulation, inspection, querying, mixed.
  - name: action_space
    type: text
    required: false
    description: The atomic actions the platform exposes and any composition rules.
  - name: ambiguity_tolerance
    type: text
    required: false
    description: How the platform should handle ambiguous, under-specified, or contradictory instructions.
  - name: safety_class
    type: choice
    required: false
    description: How autonomous the platform is and what harm a misinterpreted instruction could cause.
    choices: [research-only, supervised-tele-op, supervised-autonomy, fully-autonomous-low-risk, fully-autonomous-high-risk]
outputs:
  - name: grounding_design
    type: markdown
    description: Architecture document covering the parse-plan-act-verify loop, the schemas at each step, the refusal and ambiguity policies, the safety filter, and the evaluation methodology.
  - name: design_json
    type: json
    description: Machine-readable design with `parse_schema`, `plan_schema`, `action_whitelist`, `safety_filters`, `refusal_patterns`, `verify_checks`, `escalation_paths`, and `open_risks`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Robot VLM Instruction Grounding Architect

## When to use

Use this skill when a robotics team is designing the subsystem that turns natural-language instructions — typed or spoken by an operator, end-user, or higher-level autonomous planner — into grounded robot actions, using a vision-language model as the linguistic and perceptual interpreter. The skill produces an architecture: a four-step parse-plan-act-verify loop, the schemas exchanged at each step, the refusal patterns when the model cannot ground an instruction, the ambiguity-resolution dialogue when more than one referent matches, the safety filter sitting between the model and the motion executor, and the evaluation methodology that proves the loop is fit for the platform's safety class.

The skill is appropriate when the team has decided that natural-language instruction-following belongs on the platform and is now designing the integration. It is not the right skill for choosing a vision-language model or a vision-language-action policy; nor is it the right skill for training instruction-following data; nor is it the right skill for designing a chatbot interface that talks to a robot from the cloud — the focus here is the safety-critical bridge between language and motion.

**Mandatory safety disclaimer.** This skill produces methodology guidance for VLM-augmented robotic perception. VLMs hallucinate, miss safety-critical edge cases, and degrade in low-light, adverse-weather, and out-of-distribution conditions. Every recommendation must be reviewed by qualified roboticists, validated in simulation, and never deployed as the sole perception layer in safety-critical contexts.

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `platform_description` | yes | Anchors the design in the platform's action space and perception baseline. |
| `instruction_domain` | no | Bounds the instruction language and the supported reference resolution. |
| `action_space` | no | Defines the action whitelist the safety filter enforces. |
| `ambiguity_tolerance` | no | Drives the dialogue policy and the autonomy of disambiguation. |
| `safety_class` | no | Determines the strictness of the safety filter and the human-in-the-loop policy. |

## How to apply

The skill walks a fifteen-stage pipeline. Stages 1 through 3 frame the loop; stages 4 through 11 design each stage of the parse-plan-act-verify loop; stages 12 through 14 design the cross-cutting concerns; stage 15 produces the deliverable.

### Stage 1 — Establish the instruction surface

1. Take `platform_description` and `instruction_domain` and list the concrete instruction families the platform must support — for example, "go to <location>", "fetch <object>", "place <object> on <surface>", "describe <region>", "wait until <event>". Each family is a row in a coverage table.
2. For each family, record the *typical phrasing*, the *atypical phrasings* (synonyms, idioms, code-switching), the *misuse pattern* (a phrasing that sounds like the family but means something else), and the *out-of-scope* phrasing the platform must refuse.
3. State the *out-of-scope* boundary explicitly. The platform is not a general-purpose assistant; instructions that fall outside the supported families should be refused, not bent into shape. The refusal is itself a design output, not a failure.
4. State the *latency expectation* per family. Navigation instructions tolerate seconds of parse-and-plan; safety-critical interrupts ("stop", "back up") cannot wait for a VLM at all and route through a separate fast path.

### Stage 2 — The parse-plan-act-verify loop

5. Pin the four stages of the loop. *Parse* converts the instruction plus the current scene to a structured intent. *Plan* converts the intent plus the world model to a sequence of typed actions. *Act* executes one action at a time under the platform's existing motion control. *Verify* checks after every action whether the action achieved its postcondition and whether the broader intent still makes sense; on failure, the loop restarts at parse or plan with the updated scene.
6. State the *separation of concerns*. The VLM owns parse and partially owns plan; the platform's motion planner owns act; a separate verifier owns verify. The VLM never directly controls the actuator.
7. State the *handoff format*. Each stage's output is a typed schema that the next stage validates. Schema violation is itself a refusal pattern.
8. State the *retry policy*. The loop is not allowed to retry an unverified action without a human or a documented re-prompting step; silent retry on safety-relevant actions is the highest-cost design mistake this skill exists to prevent.

### Stage 3 — Define the action whitelist

9. List every atomic action the platform exposes — for navigation, manipulation, perception, dialogue, and any environment-affecting operation.
10. For each action, record the *preconditions* (state of the world that must hold before the action), the *postconditions* (state that must hold after if the action succeeded), the *parameters* (typed arguments and their bounds), and the *failure modes* (what happens if the action cannot achieve its postcondition).
11. Mark each action as *low-stakes*, *medium-stakes*, or *high-stakes*. Low-stakes actions (move to a nearby waypoint, describe a scene) can be authorized by the parse-plan output directly. Medium-stakes actions (open a door, place an object) require verifier sign-off. High-stakes actions (engage a tool, lift a heavy object, navigate into a regulated zone) require human-in-the-loop confirmation even when the VLM is highly confident.
12. The action whitelist becomes the contract the safety filter enforces. Any action that does not appear on the whitelist is refused by construction. The whitelist is versioned.

### Stage 4 — Parse: the schema the VLM emits

13. Design the parse schema. A robust default is a JSON object with fields: `intent_family` (enumerated, must be one of the supported families), `referents` (an array of typed scene-object descriptors with localization to be resolved by perception), `parameters` (per-family typed fields), `constraints` (operator-stated conditions like "without spilling"), `confidence` (a per-field calibrated number), and `notes` (free text the operator may see; never read by downstream).
14. Pin the *required fields* and the *forbidden patterns*. The parser refuses any output without an `intent_family` from the enumerated list, refuses any referent without a localization candidate, and refuses any output that paraphrases instead of structuring.
15. Pin the *unknown* and *refuse* values. The parse schema explicitly allows a `refuse` intent with a typed reason: out-of-scope, ambiguous, unsafe, unsupported. The downstream loop is designed to handle all four as first-class outcomes.
16. Pin the *prompt template*. The VLM's system prompt names the platform, lists the supported intent families, gives the parse schema, lists the forbidden behaviours (no free-form action invention, no bypassing the schema, no fabricating referents), and requires temperature-0 single-sample output.
17. Pin the *image conditioning*. The parse step typically takes the current front-camera frame plus the textual instruction; if the platform has multiple views, the system prompt names which views are attached and in what order. Arbitrary view selection at runtime is forbidden.

### Stage 5 — Parse: referent resolution

18. Define how parse-step referents are linked to scene-object instances. The parse output describes referents in language ("the red mug on the second shelf"); the linking step matches each referent to detected scene objects from the perception stack.
19. Design the linker. A robust pattern is a two-pass linker: first, restrict scene-object candidates by the closed-vocabulary class hint ("mug"); second, score each candidate against the full referent phrase using a vision-language similarity model; third, gate by geometric constraints from the operator phrase ("on the second shelf").
20. Specify the *no-match* and *multi-match* behaviour. No-match triggers an ambiguity dialogue with the operator or a refusal. Multi-match above a confidence-difference threshold triggers a dialogue ("did you mean A or B?"); multi-match below the threshold may trigger an autonomy default (always the leftmost, always the nearest) only for low-stakes actions, never for high-stakes.
21. Specify the *referent persistence*. Referents resolved at parse-time may drift by the time the action executes; the linker re-checks the referent at verify-time and refuses if the reference has moved beyond a class-specific tolerance.

### Stage 6 — Plan: typed action sequence

22. Design the plan schema. A plan is a sequence of typed atomic actions from the whitelist, each with bound parameters, each with the precondition it expects to satisfy, and each with the postcondition it expects to achieve.
23. Define the *planner topology*. The plan can be authored by the VLM directly (one model emits both parse and plan), by a deterministic planner consuming the parse output, or by a hybrid (VLM proposes, deterministic planner validates and re-orders). Deterministic-planner-on-top is the default for production because it isolates the safety-critical sequencing decisions from the generative model.
24. Specify the *plan-validator*. Before any plan executes, a validator walks the sequence and checks: every action is on the whitelist, every parameter is in bounds, the precondition of each step is achievable from the world state after the prior step, no step targets a referent that has not been resolved, no high-stakes action is in the sequence without a human-confirmation gate.
25. Specify the *replan trigger*. A plan that has been validated is not immutable; mid-execution, the verifier may invalidate a step (the referent has moved, a precondition is no longer met), at which point the loop returns to plan with the updated world state.
26. Specify the *plan-length cap*. Long plans hide errors; the platform caps the number of steps per plan and forces a re-parse to extend. The cap is platform-specific and is justified in the design.

### Stage 7 — Act: the bridge to motion control

27. Define the *act API*: a typed call into the platform's motion-planning subsystem. The act step does not interpret the action; it dispatches it. Any interpretation belongs in plan or in the deterministic motion planner.
28. Define the *act preflight*. Before dispatching, the act step re-confirms preconditions against the latest world state. Preconditions that have decayed since plan time trigger a replan.
29. Define the *act timeout*. Each action has a maximum execution time; on timeout, the verifier is invoked with a "timeout" status and the loop decides whether to retry, replan, or refuse.
30. Define the *interruptibility contract*. Every action accepts a cancel signal from the safety filter or the operator within a stated latency. Non-interruptible actions are forbidden on platforms above the supervised-tele-op safety class.

### Stage 8 — Verify: postcondition and intent checking

31. Design the verify step. After every action, the verifier checks two things: the *action postcondition* (did the action accomplish its local goal?) and the *intent invariant* (does the higher-level instruction still make sense, given the current world state?).
32. Define the *postcondition check sources*. Postconditions are checked against deterministic perception (gripper-state sensors for a grasp, odometry for a navigation step, freespace polygon for an "is the path clear" step), and only where deterministic perception is unavailable are they checked against the VLM. The VLM as a verifier is a fallback, not the default.
33. Define the *intent invariant*. The original instruction is re-presented to the loop after every step; if the world state contradicts the instruction (the operator said "without disturbing the table" and a tracker detects an object moved on the table), the verifier raises a violation.
34. Define the *escalation on violation*. Postcondition violations on low-stakes actions trigger a replan; on medium-stakes a refusal back to the operator; on high-stakes an immediate safe-stop and human confirmation before continuing.
35. Define the *verify-step latency budget*. Verify runs after every action, so its latency is multiplied across a plan. Keep verify deterministic where possible.

### Stage 9 — Refusal patterns

36. Catalogue the refusal patterns the loop emits: *out-of-scope* (instruction does not match a supported family), *unsafe* (instruction would require a high-stakes action without confirmation, or a forbidden action), *ambiguous* (multiple referents match), *unresolvable* (a referent in the instruction has no scene match), *infeasible* (the plan cannot be constructed under current constraints), *uncertain* (model confidence below a calibrated threshold).
37. Pin a *refusal response* for each pattern. Refusal is always paired with a structured explanation the operator can read and a suggested clarification. Silent refusal is forbidden; the loop must always emit something the operator can act on.
38. Pin the *refusal-vs-clarify policy*. For ambiguous instructions, the loop prefers clarification ("did you mean A or B?") over refusal when the dialogue is short and the ambiguity is mechanical; it prefers refusal when the ambiguity touches safety or out-of-scope.
39. Pin the *refusal logging*. Every refusal is logged with its pattern, the model output that triggered it, and the operator's follow-up. The refusal log is the most valuable training signal for the next iteration of the design.

### Stage 10 — Ambiguity resolution

40. Specify the ambiguity-resolution policy by safety stake. Low-stakes ambiguity (a "describe" instruction with two candidate regions) may be resolved autonomously by the loop. Medium-stakes (a "pick up the cup" instruction with two cups) must be resolved by a clarifying dialogue. High-stakes ambiguity is refused.
41. Specify the *clarifying-question template*. The loop generates a clarifying question grounded in the scene ("did you mean the blue mug near the toaster or the white mug near the sink?"), not a generic question ("which one?"). The grounding requires the perception layer's referents to be available in the parse output.
42. Specify the *clarification timeout*. A clarification that does not receive an operator response within a stated window resolves to refusal, not a default. The default-on-timeout pattern is forbidden by default on platforms above the supervised-tele-op safety class.
43. Specify the *dialogue depth cap*. The loop holds at most K clarification turns per instruction; beyond K, the loop refuses with "could not resolve" and asks the operator to rephrase.

### Stage 11 — Safety filtering between language and motion

44. Design the safety filter as a separate component, owned by a different reviewer than the perception or VLM teams. The filter sits between plan and act; it can reject a plan but not modify it.
45. Specify the *filter rules*: action is on whitelist; parameters are in bounds; high-stakes actions have human confirmation; no action targets a forbidden zone or a forbidden referent type; no plan contains a sequence whose pairs of actions appear on a *forbidden-pair* list (e.g. "release object" followed by "drive forward" without an intermediate "is path clear").
46. Specify the *forbidden-instruction* list. Some instructions are categorically refused before parse — instructions that name a person to harm, instructions that request the platform exceed its rated capacity, instructions that bypass safety hardware. The forbidden list is short, explicit, and reviewable.
47. Specify the *jailbreak-resistance* discipline. The filter does not consult the VLM. The filter is deterministic, code-reviewed, and tested against a known catalogue of prompt-injection patterns. Any change to the filter is a deployment with regression tests.
48. Specify the *override path*. There is exactly one override path, controlled by a named role (typically a senior operator or a safety officer), with a recorded reason. Overrides are logged and audited.

### Stage 12 — Prompt and system-message discipline

49. Pin the system prompt as a versioned artifact. It names the platform, lists the supported intent families, lists the action whitelist, names the forbidden behaviours, gives the schemas, and names the refusal patterns.
50. Pin the *injection defence*. Operator instructions are untrusted text that the platform must treat as data, not as instructions to the model itself. The system prompt explicitly instructs the model to refuse meta-instructions that attempt to modify the system prompt or the schemas.
51. Pin the *internationalization* policy. If the platform supports multiple languages, every supported language has a translated, reviewed system prompt and a parallel evaluation set. Machine-translated prompts without human review are forbidden for production.
52. Pin the *change review*. Every change to the system prompt or the schemas is reviewed by perception, safety, and product roles before deployment.

### Stage 13 — Evaluation methodology

53. Build an instruction-grounding evaluation suite with four tiers. Tier 1 is a *referent-resolution* benchmark of (image, instruction, ground-truth referent) triples. Tier 2 is a *plan-correctness* benchmark of (instruction, world-state, ground-truth plan) triples. Tier 3 is an *adversarial* set of jailbreak prompts, ambiguous referents, out-of-scope instructions, and prompts that mimic supported families but are not. Tier 4 is an *end-to-end* simulator suite where the loop runs in a simulated environment and metrics include task success, refusal rate by pattern, average dialogue turns, and rate of safety-filter activation.
54. Define the *acceptance metrics*. Per-family success rate, refusal-precision (refusals on instructions that should be refused), refusal-recall (refusals on instructions that should be refused), false-execution rate (the loop acted on an instruction it should have refused), and clarification efficiency.
55. Define *regression gates*. A new model version, a prompt change, or a schema change runs against all four tiers and must meet or exceed the prior version on safety-relevant metrics; non-safety metrics may regress only with explicit sign-off.
56. Define *failure-case capture*. Every operational failure is converted into a test case and added to the relevant tier. The evaluation suite grows with the deployment.

### Stage 14 — Observability, lifecycle, and risk

57. Specify the per-instruction telemetry: instruction text, image hash, parse output, plan output, validator decisions, safety-filter decisions, action outcomes, verify-step outcomes, dialogue turns, final disposition, operator override.
58. Specify the drift monitors: a statistically significant shift in any pattern's refusal rate, a shift in clarification frequency, a shift in plan length, all signal that the loop's behaviour is changing and warrants review.
59. Specify the model-upgrade procedure: shadow on production traffic for a defined window, then advisory, then full engagement, with rollback always available within one mission cycle.
60. Enumerate residual risks: prompt-injection from operator chat, schema drift across model versions, referent-resolver dependency on a perception layer with its own failure modes, dialogue-loop loops on persistently ambiguous environments, and the inherent risk that a generative model's behaviour cannot be exhaustively specified.

### Stage 15 — Compose the deliverable

61. Open with a one-paragraph design intent: what the platform can do with natural language, what it will refuse, what its safety stance is.
62. Render the four-stage loop with the schemas at each handoff and the validator at each boundary.
63. Render the action whitelist as a table with stakes-marking and confirmation policy.
64. Render the refusal patterns table.
65. Render the evaluation-suite tier table.
66. Emit `design_json` with structured fields for the schemas, whitelist, filters, refusal patterns, verify checks, and escalation paths.
67. Close with the mandatory safety disclaimer restated, an open-risks list, and pointers to the perception-stack architect skill and the multimodal-evaluation skill for adjacent decisions.

## Outputs

The skill returns:

1. `grounding_design` (markdown) — full architecture document for the parse-plan-act-verify loop.
2. `design_json` (JSON) — structured plan suitable for downstream automation.

## Examples

**Input (placeholder):**

`platform_description`: "Lab manipulator on a fixed base, 6-DoF arm with a parallel-jaw gripper, RGB-D camera. Operators are graduate students; instructions are typed."

`instruction_domain`: "Manipulation: pick, place, push, hand-over; perception: describe, count, find."

`action_space`: "move_to_pose, open_gripper, close_gripper, lift, push, describe_scene, locate_referent."

`ambiguity_tolerance`: "Ask a clarifying question for ambiguous referents in medium-stakes; refuse for high-stakes."

`safety_class`: "supervised-autonomy."

**Plan (abbreviated):**

- Loop: parse (frontier VLM with structured-output prompt) → linker against RGB-D scene → deterministic planner produces typed action sequence → safety filter checks whitelist and bounds → motion controller executes → verifier checks postcondition (gripper-force, object-in-hand sensor) and intent invariant.
- Schemas: parse emits `intent_family` from {pick, place, push, hand_over, describe, count, find, refuse}, with referents typed as scene-object descriptors.
- Whitelist: 7 atomic actions; lift and push marked medium-stakes requiring verifier sign-off; no high-stakes actions on this platform.
- Refusal patterns: out-of-scope (operator asks the arm to "make me coffee"), ambiguous (two red mugs visible), unsafe (operator asks to grasp something tall enough to topple), uncertain (parse confidence below threshold).
- Ambiguity: clarification dialogue grounded in scene ("the blue mug near the spectrophotometer or the blue mug on the cart?"), cap of 2 dialogue turns.
- Safety filter: enforces whitelist and parameter bounds; no override path on this platform (research class).
- Evaluation: 200 referent-resolution triples from lab photos, 50 plan-correctness scenarios in simulation, 30 adversarial prompts, end-to-end simulator runs across 15 scenes with task-success metric.

**Output excerpt:** the markdown design plus a JSON object whose `parse_schema` enumerates the structured fields, whose `safety_filters` enumerate the deterministic checks, and whose `refusal_patterns` enumerate the supported refusals with their response templates.

## Limitations

- The skill produces an architecture and methodology, not a working system. Schema implementations, planner code, and motion-control integration are out of scope.
- The skill does not encode any specific model's prompt formatting; the system prompts described are templates that the team must port to whichever frontier model they integrate.
- The skill is conservative by safety class. Research platforms may relax dialogue depth and refusal patterns; production platforms should not without an explicit safety case.
- The skill does not address voice-input front ends, automatic speech recognition, or speaker-recognition; those are upstream concerns.
- The skill assumes the perception stack provides scene-object detection and localization. Without that, referent resolution cannot run and the loop reduces to free-form refusal.
- The skill does not encode jurisdiction-specific regulatory constraints on autonomous decision-making; the team must layer those on top.

## Sources reviewed

- https://github.com/openvla/openvla (MIT)
- https://github.com/IDEA-Research/GroundingDINO (Apache-2.0)
- https://github.com/facebookresearch/segment-anything (Apache-2.0)
- https://github.com/facebookresearch/sam2 (Apache-2.0)
- https://github.com/haotian-liu/LLaVA (Apache-2.0 code; research-only model checkpoints)
- https://github.com/mlfoundations/open_clip (MIT)
- https://github.com/openai/CLIP (MIT)
