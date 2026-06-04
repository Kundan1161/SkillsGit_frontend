---
id: skillsgit-curated/llm-feature-spec-author
version: 1.0.0
name: LLM Feature Spec Author
description: Author a PRD-style specification for an LLM-powered product feature — user job, IO contract, eval set, guardrails, escalation paths, UX for uncertainty, latency budget, model fallback, and success metrics.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: productivity
tags: [niche:ai-product-design, llm, prd, feature-spec, guardrails, ai-ux, success-metrics, scoping]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, claude-haiku-4-5, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: []
  tools_optional: [web_search, file_io]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - llm feature spec
  - ai feature prd
  - spec an llm feature
  - ai product requirements
  - llm prd
  - generative feature spec
  - chatbot spec
  - ai feature design
  - copilot spec
  - llm guardrails spec
  - model fallback plan
  - ai ux for uncertainty
example_invocations:
  - "Write a PRD for an LLM feature that drafts replies in our customer-support inbox."
  - "Spec an AI summarisation feature for our document app — include guardrails and a fallback plan."
  - "Help me author a feature spec for an AI assistant that suggests next steps inside a CRM."
  - "I have a rough idea for an in-app AI feature. Turn it into a complete product spec the team can build against."
inputs:
  - name: feature_idea
    type: text
    required: true
    description: A description of the LLM feature being scoped — the user problem, the proposed approach, and where the feature sits in the product. One paragraph minimum.
  - name: user_research_notes
    type: text
    required: false
    description: Quotes, interview snippets, support tickets, or analytics findings that anchor the feature in a real user job.
  - name: existing_eval_data
    type: text
    required: false
    description: Any current evaluation set, judge rubric, or labelled examples already available. If present, the spec references rather than re-invents them.
  - name: stack_constraints
    type: text
    required: false
    description: Constraints on the model stack — required model vendor, on-prem requirement, no third-party judges, latency ceiling, cost ceiling, regulated content, etc.
  - name: target_release_window
    type: text
    required: false
    description: When the feature needs to ship. Drives the staged rollout plan and which gates can be soft vs hard.
outputs:
  - name: feature_spec
    type: markdown
    description: The full LLM feature specification — user job, IO contract, eval set design, guardrails, escalation paths, UX for uncertainty, latency budget, fallback plan, rollout, success metrics, open questions.
  - name: spec_summary
    type: json
    description: Structured summary with `user_job`, `io_contract`, `eval_strategy`, `guardrails`, `escalation`, `latency_budget_ms`, `fallback`, `rollout_plan`, `success_metrics`, `open_questions`.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# LLM Feature Spec Author

## When to use

Use this skill when a product team is shipping a feature that has a language model in its critical path and the team needs a real product specification, not just a prompt and a vibe. The skill produces a PRD-style document tailored to the realities of LLM products — probabilistic outputs, latency variance, guardrail design, escalation paths, model swaps, and the success metrics that survive a model upgrade.

The skill applies to chat features, in-line completions, summarisation, drafting and rewrite features, classification and extraction features, retrieval-augmented assistants, agentic workflows that act on the user's behalf, and any other feature where an LLM is the engine. It is not the right skill for choosing between candidate models in a bake-off, for writing the prompts themselves, or for writing the evaluation harness in detail — those are dedicated skills. This skill writes the product spec the eval harness, prompt library, and engineering plan all reference.

The skill is also not the right tool for a generic non-AI PRD. The non-AI PRD assumes deterministic behaviour; the LLM feature spec must explicitly plan for variance, refusals, hallucinations, latency tails, model deprecations, and the UX of "I am not sure".

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `feature_idea` | yes | Anchor for every downstream decision. |
| `user_research_notes` | no | Grounds the user job and prevents "AI feature in search of a problem". |
| `existing_eval_data` | no | Lets the spec reference labelled examples instead of inventing them. |
| `stack_constraints` | no | Limits which model fallback and judge options are viable. |
| `target_release_window` | no | Decides which gates are blocking vs aspirational at launch. |

## How to apply

The skill walks through a deterministic twelve-stage pipeline. Each stage produces a section of the deliverable. Stages may surface open questions; the spec records them rather than guessing.

### Stage 1 — Frame the user job

1. Read `feature_idea` and `user_research_notes` and write a one-paragraph "job statement" in the form *when [situation], the user wants to [motivation] so they can [outcome]*. The job is the user's goal in the user's words, not the team's solution.
2. List three to five alternative ways the user solves this today without the feature. If the alternatives are all already adequate, the feature is a "nice-to-have"; mark it as such and proceed with eyes open.
3. Identify the moment in the product where the feature triggers. Be specific: a button click, a route load, an empty state, an asynchronous batch, a webhook. The trigger location decides the latency budget downstream.
4. Identify the audience segment and write down its rough size, frequency of trigger per user per week, and what counts as success from the user's point of view. "Saves time" is not a success criterion; "completes the reply in under sixty seconds without the user editing the body" is.
5. Pin one anti-job — something the feature must *not* try to do — to keep scope honest. The most common useful anti-job is "do not do work the user has not explicitly authorised".

### Stage 2 — Define the IO contract

6. The IO contract is the function signature the rest of the product reasons about. Write it as a structured block with inputs, outputs, side effects, and invariants.
7. Inputs: list every field the model will see, the field type, the source (user-typed, retrieved, system-provided), and whether the field can contain user-controlled content (a prompt-injection risk).
8. Outputs: list every field the model produces and the strict format. If the output is structured (JSON, function call), include the schema. If the output is free text, define the constraints — maximum length in tokens, required sections, forbidden phrases, language.
9. Side effects: does the feature send a message, write to a database, call a tool, take an action on a third-party? Each side effect is a separate failure mode and a separate guardrail question (Stage 6).
10. Invariants: properties the output must always satisfy regardless of input. Format adherence, no PII echo, no destructive operations, refusal on disallowed requests. Invariants become gates in the eval harness.
11. Determinism expectations: declare which fields must be stable across re-runs (temperature zero, seed pinned, structured output mode) and which may vary. Users who see a different answer each time they retry will not trust the feature.

### Stage 3 — Source of truth for grounding

12. For any feature whose correctness depends on knowledge beyond the model's parameters, name the source of truth. Examples: a help-centre corpus, the user's own documents, a CRM record, a vendor catalogue.
13. For each source, record how it is retrieved (semantic search, exact lookup, structured query, full inclusion), the staleness tolerance, and the access scope (user-scoped, tenant-scoped, global). A retrieval feature with wrong scoping is a data-leak feature.
14. If no external grounding is needed because the task is purely linguistic (rewrite, translate, summarise the input the user provided), say so explicitly. "No grounding required" is a valid answer that prevents over-engineering.
15. Spell out what happens when the source of truth contradicts the model's prior. The default and almost always correct answer: the source of truth wins, the model is instructed to refuse rather than make something up, and the UX surfaces "I could not find this".

### Stage 4 — Evaluation strategy

16. The spec references the eval harness rather than designing it in full (see the dedicated harness-design skill for that). What the spec must commit to is the *strategy*: which sub-qualities will be evaluated, what the gates and axes are, and the rough size of the test set.
17. Decompose the IO contract's invariants into evaluatable sub-qualities. For each, decide gate vs axis. Gates block release; axes trade off and are tracked over time.
18. Identify which sub-qualities can be evaluated programmatically (format check, schema validation, classifier output) and which require an LLM-as-judge or human review. Cheap-and-deterministic metrics go first; expensive judges are reserved for the qualities that actually need them.
19. Commit to an initial test set size and how it will grow. A typical first cut is a thirty-example smoke set plus a two-hundred-example regression set with slices for the top user segments and the top failure modes.
20. Name the baseline. "We will measure improvement against today's behaviour" is meaningless without a recorded baseline run on a frozen test set; the spec captures that the baseline must be measured before the feature ships.
21. Name the regression bar. A common shape: no gate metric drops below its launch threshold, no axis metric drops by more than a defined delta on any tracked slice, and any drop triggers an automatic rollback or hold.

### Stage 5 — UX for uncertainty

22. LLM features are probabilistic. The UX must accommodate "the model is not sure", "the model is wrong", and "the model refused". The spec names the pattern for each.
23. **Confidence surfacing.** Decide whether the feature shows a confidence signal at all. Most user-facing surfaces should not show a raw probability — they are unintuitive and false-precise. Better signals are categorical: "high confidence", "best guess", "unsure — please verify". The signal must be earned, not invented; if there is no calibrated source for it, do not show it.
24. **Edit-before-send.** For any feature where the model produces content the user will share or act on (reply drafts, generated documents, suggested actions), the default UX is "draft, never auto-send". The user reviews before commit. State the default explicitly so engineering does not auto-send to save a click.
25. **Refusal UX.** Decide what happens when the model refuses. A blank screen is the worst outcome. The default: a short explanation, a manual fallback path, and a feedback button. The refusal UI must not leak the system prompt.
26. **Streaming vs batched.** Decide whether the output streams character by character or appears as a complete result. Streaming reduces perceived latency for long outputs but is wrong for structured outputs the UI cannot render partially. Pick once and document.
27. **Show-your-work.** Decide whether the feature exposes its reasoning, retrieved sources, or tool calls. Citations are usually a win for trust. Raw chain-of-thought is usually a loss. Default to "sources yes, internal reasoning no" unless the use case is research or compliance.
28. **Recovery affordances.** Always include a way to retry, regenerate with different instructions, or escape to a non-AI path. A feature with no escape hatch is one the user will route around.

### Stage 6 — Guardrails

29. List the guardrails the feature requires. Each guardrail is named, has a defined trigger, an enforcement mechanism, and an observable outcome.
30. **Input guardrails.** Prompt-injection detection on user-controlled fields that flow into the system prompt. Content-policy classification on free-text inputs. Rate limiting per user and per tenant.
31. **Output guardrails.** Format validation (parse the JSON, check the schema, check required fields). Content-policy classification on outputs. PII redaction if the feature operates on sensitive data. Toxicity or refusal-correctness checks where relevant.
32. **Tool-call guardrails.** For any feature that triggers a side effect (sending an email, writing to a database, charging a card), define the allow-list of permissible actions, the parameter validators, and which actions require explicit user confirmation. The default for irreversible or financially-significant actions is "always confirm".
33. **Loop guardrails.** For agentic features, set hard ceilings on number of tool calls per turn, tokens per turn, wall-clock per turn, and total cost per turn. A feature that can spend ten dollars on one invocation is a feature that will, somewhere.
34. **Data-handling guardrails.** Declare which fields may be sent to which model providers. Declare retention policies on prompts and outputs. Declare which models may be used for which tenants if data-residency constraints apply.
35. Every guardrail has a metric in the eval harness or in production observability. A guardrail without a metric is a comment.

### Stage 7 — Escalation paths

36. Every LLM feature has cases it should not try to handle. The spec names the escalation paths.
37. **To a different model.** A more capable model (and slower, more expensive) for hard cases. The escalation trigger is a classifier or a confidence signal; the budget per escalation is named.
38. **To a different tool.** Hand off to a deterministic system (a structured search, a database query, a rules engine) when the task is better solved without an LLM.
39. **To a human.** A queue with an SLA. The escalation trigger is named (low judge score, user feedback, guardrail violation, novel input type). The handoff captures the original input, the model output, and the reason for escalation.
40. **To "no answer".** A clean refusal with a manual path. Better than a confident wrong answer.
41. Track the rate of each escalation in production. A sudden spike is a regression signal.

### Stage 8 — Latency and cost budget

42. Pin a latency budget at the trigger location. Foreground interactive features need a perceived latency target (time to first token for streaming, time to result for batched). Background features can have a much looser budget.
43. Decompose the budget by component: retrieval, prompt assembly, model inference, output parsing, guardrail checks, downstream side effects. Each component gets a sub-budget.
44. Pin a per-invocation cost budget in fractional cents. Compute it against the expected daily call volume from Stage 1 to get a monthly cost ceiling. If the monthly cost exceeds the expected revenue or the willingness-to-pay of the audience, redesign before building.
45. Identify which optimisations are available if the budget is missed: shorter prompts, smaller model, cached retrievals, batched calls, asynchronous mode. Listing them now beats discovering them under pressure.

### Stage 9 — Model fallback plan

46. The model the feature ships on will be deprecated. Plan for it.
47. Name the primary model and one or two compatible fallbacks. The fallbacks should differ in vendor and in capability tier so any single outage or deprecation is survivable.
48. Specify which sub-qualities the fallback must continue to satisfy. If the primary is needed for a specific capability that the fallback lacks (long context, vision, tool use), record what degrades on fallback and what UX change accompanies the degradation.
49. Define the switchover mechanism: a feature flag, a config change, an automatic circuit breaker on error rate, or all three. A "we will deploy a fix" plan is not a fallback plan.
50. Schedule a fallback drill. At least once per quarter, route a fraction of traffic to the fallback and re-run the eval harness against it. Drift in the fallback is a silent failure mode.

### Stage 10 — Rollout plan

51. Pick the rollout shape. A staged rollout is the default: internal dogfood, beta cohort, percentage rollout, general availability. Each stage has entry and exit criteria.
52. Entry criteria for each stage: gate metrics green on the eval set, no open critical bugs, observability in place. Exit criteria: at least N invocations observed, user-reported issues below a threshold, latency and cost within budget.
53. Define the kill switch. A single config that disables the feature in production without a code deploy. The kill switch is wired into the rollout plan before the first beta cohort, not after the first incident.
54. Identify the smallest reversible step. If the rollout is wrong, what is the cost of pulling back? If the answer is "we have to email everyone and apologise", reduce the blast radius before launching.

### Stage 11 — Success metrics

55. Pin three to five top-line metrics. Each metric must be measurable, comparable to a baseline, and unambiguous about what direction is good.
56. **User behaviour.** Activation (did the user trigger the feature), completion (did the invocation end in an accepted output), retention (does the user return). Avoid vanity metrics like "AI sessions" that conflate trying once with actually using the feature.
57. **Quality.** Acceptance rate (did the user keep the output unedited or with light edits), edit distance for editable outputs, explicit thumbs feedback if collected. Quality metrics complement the eval harness but must not be the only quality signal.
58. **Business.** A leading indicator for the user job — time to first reply for a support feature, conversion rate for a marketing feature, retention for an onboarding feature. The business metric ties the feature to a revenue or cost story the team can defend.
59. **Counter-metrics.** Things that must not get worse. Latency on the host page, error rate, downstream support contact volume, refund rate. A win on the headline that breaks a counter-metric is not a win.
60. Decide the measurement window per metric. Some metrics stabilise in a day; others need two release cycles. The spec records the window so nobody calls a result early.

### Stage 12 — Open questions and risks

61. List the open questions the spec could not answer. Each open question has an owner, a path to resolution (research, prototype, vendor call, legal review), and a date by which the answer is needed.
62. List the top three risks. For each risk, name the probability, the impact, the mitigation already in the spec, and the residual risk after mitigation. The risk register is short on purpose; the team must be able to read it.
63. Name the things that would cause the spec to change materially. A new model release with materially different cost, a change in regulatory posture, a major shift in the user research findings. Watching for those is part of the rollout plan.
64. End with a one-line summary that the engineering lead, the design lead, and the PM all agree captures the feature. If the three of them disagree on the one-liner, the spec is not done.

## Outputs

The `feature_spec` markdown contains, in order: a one-paragraph summary, the user job, the IO contract, the source-of-truth and grounding plan, the evaluation strategy, the UX for uncertainty, the guardrails, the escalation paths, the latency and cost budget, the model fallback plan, the rollout plan, the success metrics, the open questions and risks, and a one-line summary. The `spec_summary` JSON mirrors the same structure for machine consumption.

## Examples

A specification for an AI reply-draft feature in a customer-support inbox might pin the user job as *when a new ticket arrives, the agent wants a credible first-draft reply so they can edit and send in under sixty seconds*. The IO contract takes the incoming ticket body, the customer's last three tickets, and the knowledge-base passages retrieved for the ticket; produces a draft body and a list of cited passages; and invariants include "no PII echo beyond what the customer wrote" and "no claims unsupported by the cited passages". Guardrails include prompt-injection detection on the ticket body, a faithfulness check against the citations, and a "never auto-send" UX rule. Fallback model is the secondary vendor's mid-tier model with a degraded latency budget. Success metrics are agent edit-acceptance rate, time-to-first-reply, and a counter-metric of customer-reopened-ticket rate.

A specification for an AI document summariser pins the user job as *when a user opens a long document, the user wants a faithful one-paragraph summary so they can decide whether to read in full*. The IO contract takes the document body; produces a summary capped at a hundred and twenty words plus a list of three "topics covered"; invariants include "every sentence in the summary is supported by the document". Guardrails include length validation and a faithfulness judge. The UX surfaces a "regenerate" affordance and never shows raw confidence. Success metrics are dwell on the summary, click-through to the full document, and accept-on-regenerate ratio.

## Limitations

The skill writes a specification; it does not write the prompts, the evaluation harness implementation, or the engineering plan. It is not a substitute for user research; if the inputs do not contain real user evidence, the spec will surface "ground the job statement in research" as a top open question and proceed with placeholders.

The skill assumes a vendor-model architecture. For features built on self-trained models, the fallback plan and model-deprecation stages need to be reframed in terms of training pipelines and model registries; the rest of the spec still applies.

The skill cannot certify regulatory compliance. It flags regulated-content situations and escalates to legal review as a Stage 12 risk, but the answer must come from the team's counsel, not from the model.

## Sources reviewed

- https://github.com/openai/openai-cookbook
- https://github.com/microsoft/generative-ai-for-beginners
- https://github.com/langchain-ai/langchain
- https://github.com/run-llama/llama_index
- https://github.com/langfuse/langfuse
- https://github.com/promptfoo/promptfoo
- https://github.com/jxnl/instructor
- https://github.com/microsoft/semantic-kernel
