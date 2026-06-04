---
id: skillsgit-curated/saga-orchestrator-designer
version: 1.0.0
name: Saga Orchestrator Designer
description: Design a saga for a multi-step distributed transaction — choose orchestration vs choreography, define steps and compensations, fix idempotency keys, retries, and observability.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - niche:distributed-systems
  - saga
  - distributed-transactions
  - compensation
  - orchestration
  - choreography
  - idempotency
  - workflow
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
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - saga pattern
  - distributed transaction
  - compensating transaction
  - orchestration vs choreography
  - workflow design
  - durable execution
  - long-running process
  - multi-service transaction
  - rollback on failure
  - process manager
  - business workflow
  - 2pc alternative
  - eventual consistency design
example_invocations:
  - "Design a saga for our order checkout: reserve inventory, charge payment, allocate shipment, send confirmation."
  - "Our refund flow spans three services and currently corrupts state on partial failure — give us a saga design."
  - "Should we use orchestration or choreography for the onboarding workflow?"
inputs:
  - name: process
    type: text
    required: true
    description: The multi-step process to design. List the steps in order, the service that performs each, and the side effects each step produces.
  - name: failure_consequences
    type: text
    required: false
    description: What the business considers worst-case if a step fails — overcharged customer, oversold inventory, duplicate fulfillment, lost data.
  - name: existing_infrastructure
    type: text
    required: false
    description: Workflow engines, message brokers, databases, and SDKs already in use. Affects implementation recommendations.
  - name: time_horizon
    type: choice
    required: false
    description: How long the process can plausibly take from start to finish.
    choices: [sub-second, seconds, minutes, hours, days, weeks-or-longer]
  - name: visibility_needs
    type: text
    required: false
    description: Who needs to see the state of an in-flight process — operators, support, the user, auditors, none of the above.
outputs:
  - name: saga_design
    type: markdown
    description: A design document with the step list, compensations, idempotency strategy, retry behavior, observability plan, and a decision on orchestration vs choreography.
  - name: state_diagram
    type: markdown
    description: A text state diagram (and an optional Mermaid block) describing happy path, failure branches, and compensation paths.
  - name: implementation_notes
    type: markdown
    description: Notes for implementing the saga on the team's chosen workflow engine or messaging stack, including the few knobs that matter.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Saga Orchestrator Designer

## When to use

Use this skill when a business operation requires more than one local transaction across services or databases, and the team needs the right shape for handling partial failures. The output is a saga design — the steps, the compensations, the contract for retries and idempotency, and the call on whether to orchestrate from a central place or let services choreograph via events.

The skill is calibrated for the common case where two-phase commit is unavailable or undesirable, and the team is reaching for a saga as the substitute. It also handles the cases where a "saga" was actually written but is missing compensations, idempotency, or visibility — the skill catches those gaps and supplies the missing pieces.

Common triggers:

- A checkout flow touches inventory, payments, fulfillment, and notifications, and a partial failure produces inconsistent state.
- A refund process spans payments, ledger, and inventory return; the team has it half-built and is being burned by partial failures.
- A new long-running business process (KYC onboarding, multi-stage approval) is being designed and the team is unsure where to put the state.
- An outage left orders in a half-allocated state and there is no replay tooling.
- A workflow engine is being introduced and the team wants to model an existing process correctly.

Do not use this skill for:

- Single-service multi-table transactions; use the database's own transactions.
- Pure event-routing without a process; use the eventing-architect skill instead.
- Two-phase commit decisions across compatible databases that can actually do 2PC; that is a database topic.

## Inputs

- `process` (required) — A concrete step list. "Reserve inventory in inventory-svc, then charge in payments-svc, then allocate in fulfillment-svc, then mark order paid in order-svc, then send confirmation email via notifications-svc" is useful. "We have a checkout" is not.
- `failure_consequences` — Drives the strictness of compensation design. Overcharging a customer is worse than under-emailing.
- `existing_infrastructure` — Affects the implementation. A team with a workflow engine already operated will get a different recommendation than a team with only a queue.
- `time_horizon` — Drives durability requirements. A two-second saga can be in-memory; a two-week saga must be durable and resumable.
- `visibility_needs` — Drives observability and the choice between orchestration and choreography. Operations teams generally need a single place to see saga state; pure choreography hides that.

## How to apply

Apply the steps in order. The output document builds as you go.

### 1. Restate the process

1.1. Capture each step in the form: **step name** (verb-noun), **owner service**, **side effects**, **input dependencies**, **expected duration**.

1.2. Mark each step as **forward action** (intended business effect) or **bookkeeping** (purely informational). Bookkeeping steps still need compensations if they fan out side effects (notifications, analytics writes).

1.3. Mark each step's **failure modes**: known transient errors, business-rule rejections (e.g. insufficient inventory), validation failures, hard outages.

1.4. Re-check the order. Steps with the smallest blast radius and the easiest compensation should run last, not first, when feasible. Notifications usually go last; payments usually go before fulfillment.

### 2. Decide orchestration or choreography

2.1. The trade-off:

- **Orchestration**: a single component (the orchestrator) directs each step and reacts to results. Pros: easy to see the whole process in one place, easy to add steps, natural place for visibility. Cons: a central component to operate, risk of becoming a coupling chokepoint if it grows beyond its scope.
- **Choreography**: each service listens to events and decides whether to act. Pros: services are loosely coupled, no central component. Cons: process logic is implicit, scattered across services; observability is harder; loops and cycles are easy to introduce.

2.2. Default to **orchestration** when:

- The process has more than three steps.
- The business needs a single place to inspect in-flight state.
- The process has branching (different outcomes by business rule), not just a linear flow.
- A workflow engine is already in use.

2.3. Default to **choreography** when:

- The process is two or three steps and each is a natural reaction to the previous event.
- There is no operational need to see the process as a whole.
- The team is small and uniform; coordinating event schemas is cheaper than running an orchestrator.

2.4. Mixed approaches exist: an orchestrator drives the critical spine of the process while peripheral effects (analytics, search indexing) consume events independently.

### 3. Define the compensations

3.1. Every forward step needs a **compensation** unless it has no side effects. Compensations are not literal undo (you cannot un-send an email); they are business-meaningful reversals (you can send a "previous email was wrong" follow-up; you can refund a charge).

3.2. For each step, write the compensation in the same form: name, owner service, side effects, input dependencies. The compensation is itself a saga step; it can fail; it needs its own idempotency and retry.

3.3. Compensations are run in **reverse order** of the forward steps that completed. The orchestrator (or the choreography pattern) walks backward from the failed step.

3.4. Some compensations are **semantic** rather than literal: a "reserve inventory" step may have a TTL on the reservation rather than an explicit release; if the saga fails, time releases it automatically. Document the TTL clearly; do not rely on undocumented timeouts.

3.5. Some steps are **non-compensable in real time** (a physical shipment leaves the warehouse). For these:

- Either reorder the saga to run them last, where a failure to advance does not require the compensation, or
- Insert a **human-in-the-loop** step that confirms the irreversible action.

3.6. Distinguish **compensatable failures** (run the compensations) from **forward-recoverable failures** (retry the failed step or skip ahead). Not every failure should trigger rollback; a transient timeout on the email step does not require unwinding the order.

### 4. Define idempotency at every boundary

4.1. The saga retries; therefore every step must be idempotent. Without idempotency a retry causes a duplicate charge, a duplicate ship, or a duplicate email.

4.2. The saga assigns an **idempotency key** to each step invocation. Format: `{saga_id}:{step_name}:{attempt_kind}`. The same key is reused across retries; a new compensation gets a key with `attempt_kind=compensation`.

4.3. The downstream service deduplicates on the key. Document this in each step's contract: "the payments service deduplicates on idempotency key for at least 7 days."

4.4. For services that do not support idempotency, add a deduplication layer (a small table that records the key and the result) at the boundary of the calling service.

4.5. Beware of **partial-completion ambiguity**: a step started, performed its side effect, then failed to respond. The retry must arrive at the same downstream state. Without a deduplication record, the retry double-applies.

### 5. Define retry policy per step

5.1. Each step has its own retry policy. The saga is durable; the retries within a step are short-horizon. Do not pile durable retries on top of in-process retries blindly.

5.2. Default per step: 3 in-process attempts with exponential backoff and full jitter, then the saga marks the step as needing durable retry and re-schedules it via the workflow engine or the saga's own scheduler.

5.3. Durable retries can run for hours or days. Cap the total attempts (e.g. 50) so a permanently broken downstream does not retry forever.

5.4. Distinguish **retry on the same step** (still trying to advance) from **retry on the compensation** (still trying to roll back). Compensations retry indefinitely by default; abandoning a compensation leaves the world in a half-state, which is usually worse than retrying.

5.5. On retry exhaustion, escalate. The saga moves to a `needs_intervention` state, pages a human, and exposes context for diagnosis.

### 6. Plan durability and resumption

6.1. The saga state must survive process restarts. Options:

- **Workflow engine** with durable execution (Temporal, Cadence, Restate, Dapr Workflows). The engine handles persistence, scheduling, and retries; the application supplies pure step functions.
- **Database-backed orchestrator** with the saga state as rows and a poller. Works for low-volume sagas without a workflow engine.
- **Event-sourced** choreography where each step emits an event consumed by the next service. The state is implicit in the event log.

6.2. The choice depends on existing infrastructure and time horizon. For sub-second sagas, even an in-memory orchestrator with a fallback recovery scan is acceptable. For minutes-or-longer sagas, durability is mandatory.

6.3. Plan for **resume after crash**. The saga must be able to pick up where it left off. With a workflow engine this is built in; with a hand-built orchestrator the state machine must persist state transitions before performing side effects.

6.4. Plan for **resume after schema change**. In-flight sagas may have been started against an older step list. Either preserve the old step list per saga instance (immutable plan) or design the steps to be additively compatible.

### 7. Plan observability

7.1. Every saga instance has an id. Every log line, metric, and trace span from every step carries it.

7.2. Provide a **saga inspector**: a tool to look up a saga instance by id and see its current step, history, compensation status, retry count, last error. This is operations team-critical, not optional.

7.3. Emit metrics: sagas started, completed, failed-compensated, failed-needs-intervention, in-flight duration percentiles. Alert on completion-rate drops and on growth in needs-intervention.

7.4. Trace each step as a distributed trace span with the saga id as the trace attribute. Cross-service correlation falls apart without this.

7.5. Keep an **audit log** of every state transition. For regulated processes the audit log may itself be a deliverable.

### 8. Handle the long tail of failure modes

8.1. **Timeout at the boundary** — the caller times out, the downstream still finishes. Idempotency keys plus an explicit "ask the downstream what happened" reconciliation step handle this.

8.2. **Network partition mid-step** — same as a timeout from the caller's perspective. The reconciliation step is the same.

8.3. **Wrong-step-applied due to programmer error** — the saga ran the wrong compensation. Recovery requires a manual operator tool, not an automated path; design for the inspector to support targeted edits and document the rules.

8.4. **Stuck saga** — neither succeeded nor failed, frozen in an intermediate state. Detect with a stale-state alert: sagas in a non-terminal state for longer than the expected p99 duration are surfaced for inspection.

8.5. **Compensation cannot succeed** — the downstream is gone, the resource is unreversible, the customer has died. The saga moves to a terminal `needs_manual_intervention` state. This is a respectable terminal state; pretending an unfixable saga is fixable is the worse outcome.

### 9. Decide on patterns within the saga

9.1. **Pivot transactions**: the first irreversible step in the saga. Steps before the pivot are easy to compensate; steps after the pivot may not be. Identify the pivot explicitly and put as much validation as possible before it.

9.2. **Retryable vs non-retryable steps**: not all steps are retryable. A step that already produced an external physical effect cannot be retried; only its consequence can be confirmed.

9.3. **Conditional steps**: branching steps. Define the branching condition explicitly, with a tested code path per branch. Branches that exist only for tests rot.

9.4. **Parallel steps**: when two steps have no dependency, run them in parallel. The saga state machine becomes more complex but the wall-clock time drops. Design the failure handling carefully — partial completion across parallel branches needs explicit rules.

### 10. Plan for evolution

10.1. The saga's step list will change. Build for it from day one:

- Version the saga definition. In-flight sagas keep their definition; new sagas use the new version.
- Add steps additively first; only restructure when necessary.
- For breaking restructures, plan a migration: drain in-flight sagas on the old version, then deploy the new version.

10.2. Keep step functions **pure with respect to the saga**: a step takes input, performs side effects, returns output. Do not let steps know about the saga's overall plan; that knowledge belongs to the orchestrator.

### 11. Emit the design

11.1. Lead with a one-paragraph summary: orchestration vs choreography, the step count, the worst compensation path, the durability story.

11.2. Include the step table: step, owner, forward action, compensation, idempotency key shape, retry policy, side effects.

11.3. Include the state diagram (text plus optional Mermaid block) showing happy path, failure branches, compensation flow, and the `needs_intervention` terminal.

11.4. Include the observability plan: metrics, traces, inspector tool, alerts.

11.5. Include the implementation notes for the chosen infrastructure: which library or engine to use, the few configuration knobs that matter, and the local development story.

### Decision rules and heuristics

- **No saga without compensations.** A "saga" that only handles the happy path is not a saga; it is a hopeful pipeline.
- **Orchestration scales better than choreography past three steps.** Choreography is elegant in small examples and a nightmare in large ones.
- **Idempotency keys cover most of distributed-transaction pain.** Without them, retries are not safe; with them, most failure modes become tractable.
- **Pivot transactions reveal the design.** If the team cannot name the pivot, the design is not done.
- **Time-bounded reservations beat explicit cancels** when feasible. A reservation that expires by TTL is simpler than a compensate-on-failure call.
- **Build the inspector before the third saga.** Operators will ask for it; building it under pressure during an incident is the painful path.
- **Compensations retry forever by default.** A failed compensation that gives up leaves the system in a worse state than retrying.
- **Workflow engines pay for themselves past minutes-long sagas.** Hand-built orchestrators degrade as the saga grows.

### Edge cases

- **A step that fans out to many downstreams.** Wrap the fan-out as a single sub-saga; compensate the sub-saga as a whole.
- **A step that the user must approve manually.** Model approval as a step with a long timeout and a separate event source (the user clicking a button). The saga waits.
- **A step whose downstream is eventually consistent.** The step's success means the downstream accepted the request, not that it converged. Add a verification step after a delay or rely on downstream events to confirm.
- **A saga that touches both your services and a third party.** The third party may not support idempotency. Add an in-front reconciliation step that calls the third party's read API to confirm state before retrying writes.
- **Compensation involves charging the customer (e.g. refund).** Treat the refund as a first-class business event with its own lifecycle, not as an internal saga step. Make it visible in customer-facing systems.
- **Many sagas in flight simultaneously sharing a resource.** Resource contention can deadlock saga compensations. Either order saga execution against the resource, or accept that compensations will retry under contention until they succeed.
- **The team wants exactly-once.** It does not exist across services. Provide at-least-once plus idempotency and explain it.

## Outputs

- `saga_design` — A markdown document with the steps, compensations, retry and idempotency policies, observability plan, durability decision, and a clearly stated orchestration-vs-choreography call with reasons.
- `state_diagram` — A text representation suitable for review. A Mermaid block follows for renderers that support it. Shows the pivot, the compensation path, and the `needs_intervention` terminal.
- `implementation_notes` — Stack-specific advice for the team's existing tools, with attention to the small number of knobs that decide whether the implementation will be operable.

## Examples

### Worked example

Input excerpt:

> Checkout: reserve inventory (inventory-svc), authorize payment (payments-svc), allocate shipment (fulfillment-svc), mark order placed (order-svc), send confirmation (notifications-svc). Worst case if partial: customer charged without an order created, or order placed without inventory. Stack: Kafka and Postgres in production; no workflow engine yet. Expected duration: 1–5 seconds happy path, up to 60 seconds in degraded conditions.

Expected output sketch:

- Style: orchestration. The orchestrator runs in the order-svc; Temporal is recommended given the team's interest in adopting a durable execution engine, but a Postgres-backed orchestrator with a poller is acceptable for the first iteration.
- Steps and compensations:
  - reserve inventory → compensate by releasing the reservation (or rely on 30-minute TTL).
  - authorize payment → compensate by voiding the authorization (not capture).
  - allocate shipment → compensate by canceling the allocation.
  - mark order placed → no compensation needed if last; pivot is "capture payment" if introduced later.
  - send confirmation → no compensation; on failure, retry with backoff and surface via inspector.
- Pivot: authorize payment is the first hard step; everything before is reservation-based.
- Idempotency: keys formed as `{order_id}:{step}:forward` and `{order_id}:{step}:compensation`. All downstreams must dedupe on the header.
- Retry policy: 3 in-process attempts per step with full-jitter backoff, then durable retry every 10 minutes up to 6 hours; on retry exhaustion move to `needs_intervention`.
- Durability: workflow engine if available; otherwise Postgres-backed state with a 5-second poller, durably persist state before each step.
- Observability: saga inspector tool keyed by order id; metrics on completion-rate and compensation rate; trace span per step; alerts on `needs_intervention` count and on stuck sagas older than 5 minutes.
- Open questions: confirmation email retries — is duplicate email worse than no email? If duplicate is worse, the dedupe key applies; if missing is worse, retry aggressively.

## Limitations

- The skill assumes the team can introduce idempotency keys at every boundary. Where the downstream is a third party that does not support keys, the design degrades to "best effort plus reconciliation" and the user must accept that compromise.
- It does not pick a specific workflow engine over another; it recommends a class and lists candidates. The team must validate operational fit.
- It does not write the orchestrator code; it produces a design, a state diagram, and implementation notes.
- It is biased toward orchestration past three steps. Teams with a strong commitment to choreography can override, but the skill will flag the operational consequences.
- It cannot solve human-coordination edge cases (a customer service agent making manual changes mid-saga). It can suggest a tool to make those edits safe.

## Sources reviewed

- https://github.com/temporalio/temporal
- https://github.com/uber/cadence
- https://github.com/restatedev/restate
- https://github.com/dapr/dapr
- https://github.com/eventuate-tram/eventuate-tram-sagas
- https://github.com/apache/kafka
- https://github.com/hibiken/asynq
