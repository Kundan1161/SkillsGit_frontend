---
id: skillsgit-curated/embedded-ci-and-hardware-in-the-loop
version: 1.0.0
name: Embedded CI and Hardware-in-the-Loop
description: Design CI for firmware — build matrices, host unit tests, on-target HIL rigs, regression cohorts, and hardware allocation queues.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-embedded
    role: author
category: robotics
tags:
  - niche:embedded-realtime
  - ci
  - hardware-in-the-loop
  - hil
  - unit-testing
  - renode
  - unity
  - ceedling
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
  estimated_tokens_per_invocation: 6500
trigger_keywords:
  - embedded ci
  - firmware ci
  - hardware in the loop
  - hil
  - on-target testing
  - unit test
  - unity ceedling
  - renode simulation
  - test farm
  - regression
  - flake
example_invocations:
  - "Design CI for a firmware repo with three MCU targets and shared driver code."
  - "How do we run on-target tests in CI without a wall of dev boards?"
  - "We want a HIL rig — what should it cover and how big should the test matrix be?"
  - "Our HIL tests flake. How do we make embedded CI reliable?"
inputs:
  - name: codebase_profile
    type: text
    required: true
    description: Repo layout (mono vs multi), languages (C, C++, Rust), build system (CMake, Make, Zephyr west, PlatformIO), targets.
  - name: test_inventory
    type: text
    required: false
    description: What tests exist today — host unit tests, simulator runs, on-target smoke, integration, soak.
  - name: hardware_inventory
    type: text
    required: true
    description: Dev boards available, count of each, peripherals, instruments (DAQ, power supply, signal generator, logic analyzer), network access.
  - name: deployment_pipeline
    type: text
    required: false
    description: How releases ship today — manual flashing, OTA, factory line. Cadence of releases.
outputs:
  - name: ci_design
    type: markdown
    description: CI architecture covering host tests, simulation, HIL fixtures, scheduling, flake budget, release gates, and recommended OSS tooling.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Embedded CI and Hardware-in-the-Loop

## When to use

Use this skill when an embedded team needs to design (or rescue) a CI pipeline that actually executes meaningful tests on firmware — not just "did it compile."

Typical triggers:

- A new firmware project is starting and the CI strategy must support multiple MCU targets from day one.
- A team has unit tests on the host but no on-target verification, and field bugs are escaping.
- A test farm exists but is unreliable, slow, or starved of hardware.
- A safety review requires evidence of automated testing against representative hardware.
- A release cadence is increasing and manual QA is no longer scalable.

This skill produces a CI design: build matrix, layered tests, HIL rig structure, scheduling, flake budget, and a permissively-licensed OSS stack. It does not write Jenkinsfiles or GitHub Actions YAML, but it tells you what they need to contain.

**Safety disclaimer (mandatory):** This skill produces methodology guidance. Embedded software defects can cause physical harm in safety-critical contexts. All outputs must be reviewed by qualified embedded engineers and, where applicable, validated against the safety standard governing the deployment (ISO 26262 automotive, IEC 62304 medical, DO-178C aerospace, IEC 61508 industrial). CI is a *gate*, not a *guarantee*. A green pipeline does not certify safety — it merely reduces the chance of obvious regressions reaching the field.

## How to apply

Work the steps in order. Each layer of the pyramid catches a different class of bug at a different cost.

### Step 1 — Inventory the codebase axes

Build the test-axis matrix. Axes:

- **Targets.** Each MCU family, each board revision, each silicon variant. Treat each as a distinct cell.
- **Compilers.** GCC arm-none-eabi, LLVM, vendor toolchains. Pin versions; "GCC 12.3" is not "GCC 12."
- **Optimization levels.** `-O0`, `-Os`, `-O2`, `-O3`. At minimum, build and test at the release optimization level *and* at `-O0` for ease of debug.
- **Build flavors.** Debug, release, safety, factory, OTA-staged. Each flavor differs in features and asserts.
- **Languages mixed in.** C, C++, Rust, hand-written ASM. Each carries its own analyzer pass.
- **Configuration switches.** Kconfig flags, devicetree overlays, feature-flag macros. Sample the high-value combinations, don't try to cover all.

Output a *test matrix* — a multi-dim grid where each cell is a `(target × compiler × flavor × config)` combination. Distinguish "must build" (everything), "must unit-test" (subset), "must on-target smoke" (smaller subset), "must HIL test" (smallest subset).

### Step 2 — Layer the test pyramid

Five layers, fastest first:

1. **Static analysis.** Compiler warnings as errors, cppcheck, clang-tidy with embedded rules, scan-build, IWYU, sparse, optional MISRA enforcement via your preferred tool. Runs on every push. Budget: < 5 minutes.
2. **Host unit tests.** Driver and algorithm code compiled for the host with mocks for hardware. Frameworks: Unity (MIT) + CMock (MIT) + Ceedling (MIT) for C; GoogleTest (BSD-3-Clause) for C++; defmt + cargo test (MIT/Apache-2.0) for Rust. Coverage measured with gcov or llvm-cov. Runs on every push. Budget: < 10 minutes.
3. **Simulator / emulator tests.** Runs against a virtual board using Renode (MIT) for full-system simulation, or QEMU only where its license terms (GPL) are acceptable to your distribution — note that this skill is permissive-only, so we prefer Renode for license alignment. Tests cover boot, peripheral interaction, RTOS scheduling, ISR paths. Budget: 10–30 minutes; runs per PR.
4. **On-target smoke tests.** A small board farm runs a curated set of "does it boot, does it talk, can we flash the image" checks. Budget: 10–20 minutes per target. Runs per PR for the targets affected by the diff.
5. **HIL integration and regression.** Full hardware rig with stimulus and measurement. Runs the long-form scenarios. Budget: hours. Runs nightly or on RC builds.

Plus, off-pipeline but scheduled:

- **Long-haul soak.** 24 h+ runs to catch leaks, drift, watchdog edge cases, thermal effects.
- **Power-loss matrix.** Power yanks at random points; covered explicitly for OTA flows.
- **Stress / fault-injection.** Random-bit flips on inputs, RAM corruption via debug probe, simulated brown-outs.

### Step 3 — Make host unit tests achievable

This is the most common failure point in embedded CI. Teams "can't unit test" because hardware is bolted into the code. Fix the architecture first:

- **Hardware abstraction layer (HAL).** A thin C header that declares peripheral operations as function pointers or `static inline` calls bound by build flag. Production binds the real driver; host tests bind a mock.
- **No globals leaking peripheral state.** Use struct pointers, dependency-injected into module init functions.
- **No `volatile` registers in business logic.** All register access goes through HAL.

Once HAL is in place, every module that does not depend on physical effects is unit-testable on the host. Aim for >80% line coverage of state-machine, parser, decoder, and protocol code; less for raw HAL adapters (they're tested on target).

Tooling pattern (the de-facto stack on permissive licenses):

- Unity for assertions, CMock for auto-generated mocks from headers, Ceedling for project glue.
- Build with the host compiler (GCC or Clang) plus address-sanitizer (ASan) and undefined-behavior sanitizer (UBSan) to catch latent bugs the target ignores.
- Coverage with gcov/lcov; thresholds enforced in CI.

### Step 4 — Use simulation to widen coverage

A simulator is the only way to exercise the full firmware stack at PR speed.

- **Renode (MIT).** Full-board simulation including peripherals, networking, multi-node setups. Robot Framework integration lets tests drive the simulated board and assert on UART output, GPIO state, and timing. Strong fit for permissive-license projects.
- **Zephyr's `native_posix` / `native_sim`.** Builds the Zephyr application for the host as a Linux process with simulated peripherals. Fast, ideal for testing application logic against the RTOS APIs.
- **QEMU.** Wide platform support, but GPL — if you intend to vendor or redistribute, evaluate license fit. Pure CI usage of a host-installed QEMU is fine; vendoring it into a product is not.
- **PIO** (PlatformIO) with simulators where vendor-provided ones exist.

What simulators are good for: boot sequences, peripheral protocol logic, RTOS scheduling shape, ISR ordering, memory layout sanity, regression of bugs that don't require real-time timing.

What simulators are bad for: real-time WCET, EMI / signal-integrity bugs, sensor noise, analog behavior, peripheral silicon errata, power consumption. These belong on real hardware.

### Step 5 — Design the on-target smoke fleet

A small, redundant set of boards available to the CI runner:

- **One of every target** at minimum.
- **Two or three of the highest-traffic target** so PR throughput isn't bottlenecked by a single rig.
- **Probe per board.** A debug probe (J-Link, ST-Link, CMSIS-DAP, Black Magic Probe) lets the runner flash, halt, dump RAM/Flash, and read RTT.
- **Power control.** A relay or programmable PSU on each board so the runner can cycle power. This is the difference between "rerun the test" and "rerun on a known-clean state."
- **Console capture.** UART → USB to the runner, with timestamped logs.
- **Watchdog on the host.** If a board hangs, the host job has its own timeout and yanks power.

What smoke tests cover: boot, fail-safe, basic peripheral self-test, OTA accept-and-revert dry run, version reporting. Budget per board: small enough that the slowest target finishes in under 20 minutes.

### Step 6 — Design the HIL rig

The HIL rig differs from smoke by adding *stimulus* and *measurement*:

- **Stimulus.** Function generator, programmable PSU, environmental chamber, mechanical actuators, RF generator, simulated bus traffic (CAN, LIN, RS-485). For sensor-driven products, the stimulus *is* the test plan — define the input space first.
- **Measurement.** DAQ (oscilloscope, logic analyzer, multimeter), thermal cameras, current shunts. All instruments must be controllable from a script — typically via SCPI over Ethernet/USB or vendor APIs.
- **Closed-loop scenarios.** The host script orchestrates the rig: set inputs, send a command to the DUT, capture outputs, assert. Pass criteria are quantitative (e.g., "current draw between 18 and 22 mA at idle").
- **Coverage.** Build a scenario catalog: nominal operating points, edge cases (max load, min battery, max temperature), fault injection (open / shorted sensor, malformed bus frame). Run nightly.
- **Determinism.** Reset to a known state between scenarios. Document the reset path (power cycle vs reset pin vs OTA back to baseline).
- **Result persistence.** Every run writes a structured artifact (JSON or HDF5) with raw traces and pass/fail. Compare runs over time for drift detection.

Permissive OSS for the rig:

- Robot Framework (Apache-2.0) as the test-runner DSL — wide instrument support.
- pytest (MIT) for Python-native rigs.
- python-vxi11 (MIT) and python-ivi (MIT) for instrument control.
- LabGrid (LGPL — verify fit) is widely used for board farms but is LGPL; assess license alignment before adopting.
- Renode-on-rig hybrid: simulate parts of the system you don't have physical hardware for.

### Step 7 — Scheduling and hardware allocation

A single board cannot serve every PR in parallel. Design the queue:

- **Allocation broker.** A small service tracks which boards are free. Each CI job requests a board lease, runs, releases. Implementations: GitLab's `--with` resources, Jenkins's lockable resources, a custom MQTT-based broker. Avoid letting the CI tool race for boards.
- **Affinity rules.** A PR touching driver X is routed to a board with peripheral X attached. Other boards are skipped.
- **Cohort runs.** Multiple jobs that need the same board are batched and run in sequence on one lease, amortizing flash time.
- **Time budgets.** Each job has a hard ceiling. On overrun, the orchestrator yanks power, marks the job failed with a "timeout" label, and reclaims the board.
- **Health monitoring.** Every board reports temperature, current, voltage at idle as part of CI metadata. Anomalies promote the board to "needs attention" and remove it from the pool.

For HIL with expensive instruments, reserve nightly windows rather than per-PR access. Some teams run a fixed daily HIL pass on a release candidate rather than on every commit.

### Step 8 — Flake budget and triage

Embedded CI flakes more than software-only CI. Set a budget:

- **Quarantine.** A flaky test is auto-quarantined after N consecutive false fails (N = 3 is typical). The owning team has a fixed deadline to fix or delete it. No "skip and forget."
- **Retry policy.** At most one retry, and only if telemetry indicates a transient (e.g., probe disconnect, brown-out detected). Never blanket-retry HIL — flakes are signals.
- **Hardware vs software flake.** Tag every failure with a category. If the board failed (probe lost, voltage out of range), it's a hardware flake — fix or replace. If the test failed deterministically, it's a software bug.
- **Trend tracking.** A weekly flake report. Per-test pass rate, per-board pass rate, per-suite duration. Without this, CI silently rots.

### Step 9 — Release gates

Define exactly which checks gate a release:

- **PR merge gate.** Static analysis, host unit tests, simulator tests, on-target smoke for affected targets. Total budget: < 45 minutes.
- **Nightly gate.** All of the above plus full HIL, soak excerpts, power-loss matrix. Total budget: ~6 hours; failures block any release tagged from that day.
- **Release candidate gate.** Full HIL, full power-loss matrix, full soak, manufacturing-line dry run, OTA dry run with rollback. Plus: signature verification of the produced image with the actual signing key in a controlled environment.
- **Manual gate.** Human sign-off after reviewing test artifacts, with explicit checklist (release notes accurate, version bumped, key not compromised, no open blockers).

For safety-regulated products, the gate list is dictated by the applicable standard. Document the mapping between gate and standard requirement.

### Step 10 — Cost and capacity sizing

Estimate hardware needs early:

- **Target throughput.** PRs per day × jobs per PR × board-time per job. Provision for peak, not average.
- **Redundancy.** 2× any board that's on the merge-gate path. Failing CI because a single board's USB came loose is unacceptable.
- **Refresh cycle.** Dev boards age. Plan replacement every 18–36 months as silicon revisions evolve.
- **Instruments.** A small HIL rig with a programmable PSU, a logic analyzer, and a multimeter costs a few thousand dollars. A full thermal-chamber rig with high-channel-count DAQ is in the tens of thousands. Right-size to the product's risk profile.

### Step 11 — Produce the CI design document

Output:

1. **Test matrix.** Targets × compilers × flavors × configs, annotated with required test levels.
2. **Pyramid.** Static, host unit, simulator, on-target smoke, HIL, soak — what runs where and when.
3. **HAL boundary.** What is mocked on the host vs tested on target.
4. **Simulator selection.** Renode / native_sim / vendor, with license confirmation.
5. **Board fleet.** Boards, probes, power control, console capture.
6. **HIL rig.** Stimulus, measurement, scenario catalog, reset path.
7. **Scheduler.** Allocation broker, affinity, queueing.
8. **Flake policy.** Quarantine, retry, triage, trend tracking.
9. **Release gates.** PR / nightly / RC gates with concrete checks.
10. **Capacity plan.** Throughput, redundancy, refresh, cost.
11. **Tooling list.** Permissive OSS recommendations with license notes.

## Inputs

- **Codebase profile.** Layout, languages, build system, targets.
- **Test inventory.** What exists today.
- **Hardware inventory.** Boards and instruments available.
- **Deployment pipeline.** Release cadence and shipping path.

## Outputs

A markdown CI design document with the 11 sections above.

## Examples

> "Three MCU targets (STM32G4 motor controller, nRF52 BLE bridge, ESP32 wireless gateway), Zephyr-based, monorepo, ~15 engineers, GitHub Actions, no HIL today, ~20 PRs/day, weekly release."

Expected design (abridged):

- **Matrix.** 3 targets × 1 compiler (Zephyr-pinned arm-none-eabi-gcc + xtensa for ESP32) × 2 flavors (debug, release) × ~6 Kconfig samples = ~36 build cells. All must build per PR; subset must run.
- **Pyramid.** Static + Unity/Ceedling unit + native_sim per PR; Renode boots and protocol tests per PR; on-target smoke on one G4, one nRF52, one ESP32 board per PR (affinity-routed); full HIL nightly on a rig with PSU, logic analyzer, and CAN bus simulator.
- **Boards.** 2× G4, 2× nRF52, 2× ESP32 in the smoke pool; one each in the HIL rig with stimulus.
- **Scheduler.** GitHub Actions self-hosted runners with `--concurrency` keyed on board ID; a small Python broker (pytest fixture) leases boards.
- **Flake policy.** Quarantine after 3 false fails, weekly flake report, hardware-flake category triggers a board-health page in the CI dashboard.
- **Release gates.** PR: static + unit + sim + smoke. Nightly: HIL + 4 h soak. RC: HIL + 24 h soak + OTA dry-run with rollback on each target.
- **OSS stack.** Zephyr (Apache-2.0), Unity/CMock/Ceedling (MIT), Renode (MIT), Robot Framework (Apache-2.0), pytest (MIT), python-ivi (MIT) for instrument control, MCUboot (Apache-2.0) for OTA artifacts.
- **Cost.** ~$8k of hardware in the smoke pool + ~$15k of HIL instruments + ongoing runner hours; reviewed quarterly.

## Limitations

- This skill does not write specific CI YAML, Jenkinsfile, or Robot Framework cases. It produces architecture and policy.
- Some popular tools in the embedded ecosystem are GPL/LGPL (QEMU, OpenOCD, LabGrid). This skill preferentially recommends permissively-licensed equivalents but acknowledges trade-offs; teams must verify license fit for redistribution and product inclusion separately.
- Vendor-specific simulators and proprietary instrument libraries are out of scope.
- Safety certification artifacts (tool qualification per ISO 26262 / DO-330) are not produced — that is a specialized exercise requiring formal documentation beyond what this skill outputs.
- Cost figures are rough order-of-magnitude; real procurement requires vendor quotes.
- Always re-verify the license of any vendored test framework, simulator, or instrument driver before shipping.

## Source references (URL-only)

- https://github.com/ThrowTheSwitch/Unity
- https://github.com/ThrowTheSwitch/Ceedling
- https://github.com/ThrowTheSwitch/CMock
- https://github.com/renode/renode
- https://github.com/zephyrproject-rtos/zephyr
- https://github.com/robotframework/robotframework
- https://github.com/embeddedartistry/embedded-resources
- https://github.com/mcu-tools/mcuboot
