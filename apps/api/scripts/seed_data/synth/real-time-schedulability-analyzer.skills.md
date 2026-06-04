---
id: skillsgit-curated/real-time-schedulability-analyzer
version: 1.0.0
name: Real-Time Schedulability Analyzer
description: Analyze schedulability for a set of real-time tasks using RMA, DMA, EDF, and response-time analysis with blocking, jitter, and priority-inversion mitigation.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-embedded
    role: author
category: robotics
tags:
  - niche:embedded-realtime
  - schedulability
  - rate-monotonic
  - edf
  - priority-inversion
  - wcet
  - rtos
  - response-time-analysis
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
    - gemini-1.5-pro
  min_context_tokens: 32000
  tools_optional:
    - web_search
    - code_execution
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - schedulability
  - rate monotonic
  - rma
  - dma
  - edf
  - response time analysis
  - wcet
  - jitter
  - priority inversion
  - blocking time
  - utilization bound
  - deadline miss
example_invocations:
  - "Is this set of 6 periodic tasks schedulable under rate monotonic on a 168 MHz Cortex-M4?"
  - "Compute response-time analysis for our control loop with two blocking shared resources."
  - "Compare RMA vs EDF for our motor controller — which gives more headroom?"
  - "We see occasional deadline misses on the sensor task — diagnose the priority inversion."
inputs:
  - name: task_set
    type: text
    required: true
    description: List of tasks with period (T), deadline (D), worst-case execution time (C), release jitter (J), and priority (if fixed).
  - name: shared_resources
    type: text
    required: false
    description: Shared resources / critical sections with worst-case hold time per task, and the protocol in use (NPCS, PIP, PCP, SRP, none).
  - name: platform_assumptions
    type: text
    required: true
    description: Single core vs multi-core, preemptive scheduling, RTOS in use, tick-rate granularity, interrupt overhead per task switch.
  - name: target_policy
    type: text
    required: false
    description: Which scheduling policy to analyze (fixed-priority RMA/DMA, dynamic-priority EDF, or compare). Default fixed-priority.
outputs:
  - name: schedulability_report
    type: markdown
    description: Schedulability verdict, response-time table per task, blocking analysis, sensitivity, and mitigation recommendations.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Real-Time Schedulability Analyzer

## When to use

Use this skill when an embedded engineer needs to decide whether a proposed real-time task set will meet its deadlines on a given target — or to diagnose why a deployed task set is missing them.

Typical triggers:

- A new control loop, sensor pipeline, or motor controller is being designed and the priority assignment needs to be defended.
- A scheduler-related deadline miss is observed in soak testing and the team needs to know whether the design is *infeasible* or merely *misconfigured*.
- A choice between rate-monotonic (RMA) fixed-priority and earliest-deadline-first (EDF) dynamic-priority must be justified before code is written.
- A shared resource (SPI bus, EEPROM, log buffer) is suspected of causing priority inversion on a higher-priority task.

The skill produces analysis, not code. It assigns priorities, computes response times, identifies blocking, and recommends a protocol — but never claims certification or replaces formal timing analysis on safety-critical projects.

**Safety disclaimer (mandatory):** This skill produces methodology guidance. Embedded software defects can cause physical harm in safety-critical contexts. All outputs must be reviewed by qualified embedded engineers and, where applicable, validated against the safety standard governing the deployment (ISO 26262 automotive, IEC 62304 medical, DO-178C aerospace, IEC 61508 industrial). Schedulability bounds derived here are *necessary* but not *sufficient* — measured timing on hardware with cache and pipeline effects is the final word.

## How to apply

Walk the steps in order. Each step states the math, the assumption it relies on, and the failure mode it catches.

### Step 1 — Normalize the task set

Build a canonical table. For each task `i`:

- `T_i`: period (for periodic) or minimum interarrival time (for sporadic).
- `D_i`: relative deadline. Default `D_i = T_i` for "implicit-deadline." For "constrained-deadline," `D_i <= T_i`.
- `C_i`: worst-case execution time, with caches cold and all preemptions allowed.
- `J_i`: release jitter (max delay between event and task release).
- `B_i`: blocking time the task can suffer from lower-priority tasks holding shared resources (computed in Step 4).

Refuse to proceed if any task is missing `T`, `D`, or `C`. Average-case `C` is not acceptable. If WCET has not been measured, demand it before publishing a verdict; you can still produce a *conditional* analysis but it must be labeled clearly.

### Step 2 — Compute utilization and run the cheap bounds

Total utilization `U = sum(C_i / T_i)`. This is the first sanity gate:

- `U > 1`: infeasible under *any* policy on a single core. Stop and report.
- `U <= 1`: necessary condition met for EDF (and RMA), not yet sufficient.

For fixed-priority RMA with implicit deadlines, apply the Liu & Layland bound:

`U_LL(n) = n * (2^(1/n) - 1)`

For `n` tasks, if `U <= U_LL(n)`, the set is schedulable under RMA. `U_LL(2) ≈ 0.828`, `U_LL(3) ≈ 0.779`, `U_LL(infty) ≈ ln(2) ≈ 0.693`.

If `U` is between `U_LL(n)` and 1, the set *might* still be schedulable; proceed to response-time analysis. If `U <= U_LL(n)` you can already give a green verdict, but you should still run RTA for diagnostic value (it gives slack per task).

For EDF on implicit deadlines, `U <= 1` is necessary and sufficient on a single core. Note that EDF's *failure mode* is worse than RMA's — when EDF overloads, *every* task misses; when RMA overloads, the lowest-priority task misses first. Factor this into the policy choice.

### Step 3 — Assign priorities

For fixed-priority:

- **Implicit deadlines:** rate-monotonic. Shorter period → higher priority. Optimal among fixed-priority on a single core.
- **Constrained deadlines:** deadline-monotonic (DMA). Shorter deadline → higher priority. Optimal among fixed-priority on a single core.
- **Mixed periodic + sporadic:** treat sporadic with its minimum interarrival as period; DMA still applies.
- **Ties:** break by criticality (hard before firm before soft). Document the tiebreak.

Special cases:

- A task that runs faster than 10× the RTOS tick deserves its own scheduling tier; consider running it from a hardware-timer ISR with a small fixed body, not as a normal task.
- Tasks driven by ISRs at high rates (>1 kHz) often belong in the deferred-from-ISR worker pattern, not as standalone tasks.

### Step 4 — Compute blocking time per task

Build the resource table: resource ID, set of tasks that lock it, worst-case hold time per task, protocol.

Blocking protocols and bounds:

- **No protocol (plain mutex without inheritance).** Unbounded blocking via chained priority inversion is possible. **Reject this design** for any hard-deadline task and require remediation.
- **Non-Preemptive Critical Sections (NPCS).** While locked, preemption is disabled. `B_i = max(C_lock_j)` over all critical sections in the system (including by higher-priority tasks). Easy to implement, can be wasteful.
- **Priority Inheritance Protocol (PIP).** While a lower-priority task holds a resource needed by a higher-priority one, it inherits the higher priority. `B_i <= sum over each resource of the longest critical section among lower-priority tasks` (one CS per resource). Implemented by FreeRTOS mutexes (`xSemaphoreCreateMutex`), Zephyr `k_mutex`, NuttX mutexes.
- **Priority Ceiling Protocol (PCP / Immediate PCP).** Each resource has a ceiling = priority of the highest-priority task that uses it. A task can lock only if its priority is strictly higher than all ceilings of currently locked resources. Bounds blocking to one critical section per task and prevents deadlock. Heavier; common in AUTOSAR Classic and POSIX `PTHREAD_PRIO_PROTECT`.
- **Stack Resource Policy (SRP).** EDF-compatible analog of PCP; native to EDF analyses.

For each task `i`, compute `B_i` per the chosen protocol. Document the assumption.

### Step 5 — Run response-time analysis (RTA)

For fixed-priority with blocking and jitter, the worst-case response time `R_i` of task `i` is the fixed point of:

`R_i = C_i + B_i + sum over higher-priority j of ceil((R_i + J_j) / T_j) * C_j`

Iterate from `R_i^(0) = C_i + B_i` until convergence. Schedulable iff `R_i + J_i <= D_i` for every `i`.

For EDF on a single core, an exact test is the *demand-bound function*: the set is schedulable iff for all relevant intervals `t`,

`sum over i of floor((t + T_i - D_i) / T_i) * C_i <= t`

Restrict the intervals to deadlines within the synchronous busy period. Tools and references for EDF analysis exist in the academic literature; this skill produces the closed-form check for `U <= 1` plus the demand-bound spot-check at the critical instants.

Produce a per-task table: `T`, `D`, `C`, `J`, `B`, `R`, slack `= D - R - J`, verdict.

### Step 6 — Add platform overheads

The analysis above is on idealized math. Bake in the platform:

- **Context-switch cost.** Add to `C_i` for every task; on a Cortex-M4 with FPU, budget ~2 µs per switch with FPU lazy-stacking, ~0.5 µs without FPU. Confirm with measurement.
- **Tick-driven release jitter.** A periodic task with period `T_i` released by the RTOS tick has release jitter up to one tick. If the tick is coarse relative to `T_i`, this dominates. Either raise the tick or use a hardware timer.
- **ISR steal time.** Sum ISR durations × rates and subtract from CPU available. Equivalently, treat each interrupt source as a task with `C` = ISR cost and `T` = minimum interarrival; analyze as a top-priority task in RMA.
- **Cache and pipeline effects.** WCET measured cold gives a safe upper bound; the analysis is conservative. On Cortex-A/-R with caches, formal WCET tools (aiT, Bound-T) are common in safety-critical work.

### Step 7 — Sensitivity and headroom

For every task report:

- **Slack** in absolute time and as percent of deadline.
- **CPU headroom.** `1 - U_effective` after platform overheads.
- **WCET margin.** Maximum `C_i` increase before any task misses. Useful for predicting how much new feature work the design can absorb.

If headroom is < 20 %, recommend either policy change, resource consolidation, or a faster part. If headroom is > 50 %, the design is over-provisioned — fine for safety, wasteful for cost.

### Step 8 — Diagnose observed deadline misses

If the engagement is forensic rather than predictive, work the checklist:

1. **Confirm the miss.** Tracing tool: SEGGER SystemView, Tracealyzer, Zephyr tracing, or DWT-based custom. Distinguish "task started late" from "task ran long."
2. **Late start.** Inspect priority of the late task, all higher-priority tasks' real durations, and shared-resource holds by lower-priority tasks. Suspect priority inversion or unaccounted ISR steal.
3. **Long run.** Re-measure `C`. Suspect cache thrash from a recently added task, optimization regression, or a new path through the code.
4. **Jitter.** Inspect the release source. Tick-jitter mismatch with task period (aliasing), or an upstream ISR with rate variation, are the usual culprits.
5. **Burstiness.** Sporadic tasks with bursty arrival violate min-interarrival assumptions; re-derive `T_min` from the actual trace.

### Step 9 — Recommend mitigations

Order of preference:

1. **Fix the resource protocol.** Convert plain mutexes / binary semaphores used for exclusion to priority-inheriting mutexes, or adopt PCP if the RTOS supports it.
2. **Shorten critical sections.** Move heavy work outside the lock, copy data and process locally.
3. **Re-rank by DMA** if deadlines and periods diverge.
4. **Move a task to ISR-deferred work** if its trigger is much faster than its useful period.
5. **Split a fat task** into a fast control-loop part and a slow housekeeping part with distinct priorities.
6. **Raise the tick rate or use a hardware-timer-driven release** to cut jitter.
7. **Adopt EDF** only if the team can accept EDF's overload semantics and the RTOS supports it (Zephyr, NuttX with EDF policy on POSIX, some research builds of FreeRTOS).
8. **Increase headroom** by upgrading the CPU bin or adding a second core; multi-core scheduling has its own analysis and is out of scope here.

### Step 10 — Validate against measurement

Always close the loop:

- Instrument with a trace tool. Capture a representative 24 h soak.
- Compare measured worst-case response time per task to the analytical `R_i`. If measured > analytical, the model is wrong; find the missing source of interference or blocking.
- Repeat after every significant code change.

## Inputs

- **Task set.** Period, deadline, WCET, jitter, priority hint (if any), criticality.
- **Shared resources.** Resource id, locking tasks, hold times, protocol.
- **Platform assumptions.** Core, RTOS, tick, context-switch cost, interrupt overheads.
- **Target policy.** Fixed-priority (RMA/DMA), EDF, or compare.

## Outputs

A markdown report:

1. Task-set table (canonicalized).
2. Utilization and Liu-Layland verdict.
3. Priority assignment with justification.
4. Blocking table per task.
5. Response-time table with slack and verdict per task.
6. Platform-overhead adjustments.
7. Sensitivity / headroom summary.
8. Mitigation recommendations, ranked.
9. Validation checklist with the tracing approach.

## Examples

> "Six tasks on STM32F4 at 168 MHz, FreeRTOS 1 ms tick. T = [5, 10, 20, 50, 100, 1000] ms, D = T, C = [0.4, 1.2, 3.0, 8.0, 12.0, 50.0] ms. One shared SPI bus locked for up to 2 ms by tasks 3, 4, 5. Plain binary semaphore."

Expected analysis (abridged):

- U = 0.08 + 0.12 + 0.15 + 0.16 + 0.12 + 0.05 = 0.68. Below `U_LL(6) ≈ 0.735` → schedulable bound met, but blocking analysis required.
- Priority: RMA → task 1 highest, task 6 lowest.
- Blocking with plain semaphore: unbounded chained priority inversion. **Reject.** Recommend priority-inheriting mutex (FreeRTOS `xSemaphoreCreateMutex`).
- After PIP, `B_1 = B_2 = 2 ms` (one CS each from lower-priority bus users).
- RTA: `R_1 ≈ 0.4 + 2 = 2.4 ms < 5 ms` slack 2.6 ms. `R_2 ≈ 1.2 + 2.4 = 3.6 ms`, etc. All tasks meet deadlines with healthy slack.
- Tick = 1 ms induces up to 1 ms release jitter on task 1 (period 5 ms). Recommend either raising tick to 100 µs or releasing task 1 from a hardware-timer ISR.
- Validate with SEGGER SystemView capturing the worst-case response per task across 24 h.

## Limitations

- Single-core analysis only. Multi-core schedulability (partitioned, global, or clustered) requires additional theory not covered here.
- Assumes preemptive scheduling with negligible scheduler overhead beyond context-switch cost.
- WCET is taken as given. Cache-aware and pipeline-aware WCET estimation is out of scope.
- EDF analysis here uses the utilization bound plus demand-bound spot-checks; full exact EDF analysis on constrained deadlines requires iteration over a possibly large set of busy-period checkpoints.
- Soft-real-time (statistical QoS) analysis is out of scope; this skill is built around worst-case deadlines.
- Always cross-check against measured traces; theory bounds are necessary, not sufficient.

## Source references (URL-only)

- https://github.com/FreeRTOS/FreeRTOS-Kernel
- https://github.com/zephyrproject-rtos/zephyr
- https://github.com/apache/nuttx
- https://github.com/ARMmbed/mbed-os
- https://github.com/embeddedartistry/embedded-resources
- https://github.com/ARM-software/CMSIS_5
