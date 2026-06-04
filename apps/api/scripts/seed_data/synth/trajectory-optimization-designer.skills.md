---
id: skillsgit-curated/trajectory-optimization-designer
version: 1.0.0
name: Trajectory Optimization Designer
description: Frame a robot trajectory-optimization problem — cost, constraints, initialization, smoothing, dynamic feasibility, and real-time vs offline tradeoffs.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-robotics
    role: author
category: robotics
tags:
  - niche:motion-planning
  - trajectory-optimization
  - chomp
  - trajopt
  - ilqr
  - mpc
  - ddp
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
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - trajectory optimization
  - chomp
  - trajopt
  - stomp
  - ilqr
  - ddp
  - mpc
  - crocoddyl
  - optimal control
  - smoothing
example_invocations:
  - "Set up a trajectory optimization for a 7-DoF arm pouring water — keep jerk low."
  - "Our CHOMP trajectories penetrate obstacles; how do we tighten the formulation?"
  - "Design an MPC for a quadrotor through a forest."
  - "Warm-start TrajOpt from an RRT-Connect path — what cost terms?"
inputs:
  - name: system_dynamics
    type: text
    required: true
    description: Robot model class (kinematic, second-order rigid body, full multibody with contact), state and control dimensions, key actuator limits.
  - name: task_specification
    type: text
    required: true
    description: Start, goal (or goal set), waypoints, contact phases, time horizon, allowed deviation.
  - name: constraints
    type: text
    required: true
    description: Joint limits, torque limits, obstacle clearances, balance/stability, friction-cone, end-effector pose constraints.
  - name: real_time_budget
    type: text
    required: false
    description: Offline single-shot, batch (warm-start library), or online MPC at a control rate. Specify rate if online.
outputs:
  - name: optimization_design
    type: markdown
    description: Problem formulation with cost, constraints, decision variables, initialization, solver suggestion, smoothing/post-processing, dynamic feasibility checks, and a validation plan.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Trajectory Optimization Designer

## When to use

Use this skill when a roboticist needs to **frame a trajectory-optimization problem** — pick decision variables, write the cost, write the constraints, choose an initialization strategy, decide between offline and online (MPC), and plan a validation harness. Typical triggers:

- A sampling-based planner produces jagged motions that need smoothing into something dynamically feasible.
- A task has explicit cost-quality tradeoffs (minimum time, minimum jerk, minimum energy).
- The system has second-order dynamics or contact phases (legged locomotion, manipulation with contact).
- You need MPC at a fixed control rate (quadrotor, mobile base, whole-body control).
- An existing TrajOpt/CHOMP/STOMP setup misbehaves: infeasibility, oscillation, obstacle penetration, or runtime blowups.

This skill does **not** write a custom solver. It maps task structure to an optimization formulation and a permissively licensed reference implementation.

**Safety disclaimer (mandatory):** This skill produces methodology guidance. Robot motion-planning failures cause physical harm. Every recommendation must be reviewed by qualified roboticists, validated in simulation, and bench-tested in a safe enclosure before any deployment near people or valuable property. Treat all advice as a starting point — never deployment-ready.

## How to apply

Work the problem in the order below. Skipping straight to "which solver" is the most common cause of solver failure or unsafe outputs.

### Step 1 — Pick the problem formulation

Decide which of the three canonical formulations matches the task:

- **Direct collocation (transcription).** Discretize state and control at knot points; solver enforces dynamics as equality constraints between knots. Strong when dynamics are stiff or when you want sparse-NLP solvers (IPOPT, SNOPT-class). Good default for offline trajectory generation.
- **Direct shooting / multiple shooting.** Roll out dynamics from initial state with the control sequence; solver optimizes the control sequence. Good when integration is cheap and accurate.
- **Differential dynamic programming / iLQR.** Newton-style on Bellman recursion; native to MPC because of warm-start friendliness and fast feedback gains. Good default for online whole-body control and locomotion.

If the system has rigid contact (legged, multi-contact manipulation), prefer DDP/iLQR with contact-implicit or contact-explicit phases (libraries like Crocoddyl) over generic NLP.

### Step 2 — Define decision variables and time discretization

- **Variables.** State trajectory `x[0..N]`, control trajectory `u[0..N-1]`, plus auxiliaries for collision distances, contact forces, or phase durations.
- **Knot spacing.** Uniform is the default. Use non-uniform knots when the task has clearly distinct phases (approach, contact, retract) — give each phase its own knot density.
- **Horizon length.** For offline trajectories, the horizon is the task duration. For MPC, choose the shortest horizon that still captures the dominant dynamics; typical rule of thumb is 1–2 seconds for ground robots, 0.5–1.5 seconds for aerial vehicles, 0.3–1 second for manipulators, 1–2 seconds for legged robots.
- **Time as a variable.** If task duration is unknown (minimum-time tasks), make total time a decision variable with a regularizer to prevent collapse to zero.

### Step 3 — Write the cost function

Compose the cost from these building blocks. Each term should be (a) smooth, (b) sign-correct, (c) scaled so terms are comparable in magnitude after typical motion.

- **Smoothness:** integral of acceleration squared, jerk squared, or torque-rate squared. Jerk is usually the right knob for human-safe motion.
- **Effort:** integral of control squared, energy, or torque squared.
- **Goal tracking:** distance to goal pose at terminal knot. Weight high or move to a hard terminal constraint.
- **Obstacle clearance:** signed-distance-field (SDF) penalty, hinge-loss with margin. Avoid raw distance — use a smooth approximation so gradients exist.
- **Joint-limit margin:** quadratic penalty when within a buffer of limits, encouraging mid-range.
- **Time:** terminal time or sum-of-phase-durations for minimum-time problems.
- **Posture/nullspace bias:** distance from a preferred posture (helps redundancy resolution on >6-DoF arms).

Scaling rule: after the first valid run, divide each term by the magnitude it took at the optimum, then re-tune the *ratios* you actually care about. Solvers behave badly when one term dominates by orders of magnitude.

### Step 4 — Write the constraints

- **Dynamics:** equality constraints from the integration scheme (collocation defects, RK4 residual, etc.).
- **Joint position and velocity limits:** box constraints.
- **Torque limits:** box constraints; if you have actuator dynamics, model them as additional states.
- **Collision:** distance >= margin. Use SDF when available; otherwise FCL distance queries with smoothing.
- **End-effector pose / task:** equality at terminal knot or selected interior knots; relax to soft constraints if the solver struggles.
- **Contact:** complementarity (no force without contact, no penetration with contact). This is the hardest case — either pre-specify the contact schedule and impose equality constraints, or use a contact-implicit formulation with explicit complementarity (slow but flexible).
- **Friction cone:** linearized polytope constraints on contact forces.

Prefer **hard constraints** for safety-critical limits (joint stops, torque saturations, hard obstacle margins). Use **soft penalties** for preferences (smoothness, posture, energy).

### Step 5 — Choose an initialization

Optimization-based planners are **only as good as their initialization**. Bad init -> local minima with obstacle penetration.

- **Straight-line in joint space.** Cheap, works for free-space short motions, fails for any cluttered scene.
- **Workspace straight-line, then IK.** Better than joint-space straight-line for end-effector tasks.
- **Warm-start from a sampling planner.** RRT-Connect path -> dense interpolation -> TrajOpt smoothing. The most reliable general-purpose strategy.
- **Warm-start from previous solve.** For MPC, shift the previous solution by one control step and append a final knot. This is the standard MPC initialization.
- **Library of demonstrations.** For tasks with topological diversity (e.g., reach over vs reach under), keep a small library of seeds and run the optimizer from each, then pick the lowest-cost feasible result.

### Step 6 — Solver selection and reference implementations

Map formulation to solver and library:

- **CHOMP / STOMP** — gradient-based covariant smoothing. Built into MoveIt 2 (BSD-3-Clause). Strong on smoothness, weak on hard constraints.
- **TrajOpt-style sequential QP / SLSQP / IPOPT-backed direct collocation** — Drake (BSD-3-Clause) is the reference. Strong on hard constraints, needs good init.
- **iLQR / DDP** — Crocoddyl (BSD-3-Clause) is the reference for whole-body and locomotion. Drake also provides a DDP solver. Strong for MPC.
- **Model-predictive path integral (MPPI)** — sampling-based MPC, no gradients required. Useful when dynamics are non-smooth (granular media, rough terrain). Reference implementations exist in research repos; verify licenses individually before use.

When in doubt: prototype offline with direct collocation in Drake; once the formulation is stable, port to iLQR/DDP in Crocoddyl for real-time.

### Step 7 — Smoothing and post-processing

The optimizer's output is rarely directly executable. Apply, in order:

1. **Resample** onto the controller's rate.
2. **Time parameterization.** TOTG (time-optimal trajectory generation), Ruckig (jerk-limited), or parabolic blends. Re-time so velocity/acceleration/jerk are within hardware limits.
3. **Final feasibility pass.** Re-check joint, torque, and collision constraints on the resampled trajectory; the resampler can introduce small violations near switching points.
4. **Safety margins.** Add a runtime guard: command-execution must be aborted if measured tracking error exceeds a threshold.

### Step 8 — Real-time vs offline decision

- **Offline.** Solve once, execute open-loop with a tracking controller. Acceptable only when the environment is fully known and static between plan and execute.
- **Online MPC.** Re-solve every control cycle from current state. Required for dynamic environments, contact uncertainty, or modeling error. Cycle time budget must allow >= one full DDP iteration; otherwise switch to learned warm-starts or shorter horizons.

For online MPC: always carry a **safe fallback policy** (slow halt, retract, hand-off to a low-level reactive controller) for when the optimizer fails to return a solution within the cycle.

### Step 9 — Validation plan

Refuse to call the design "done" until the user commits to:

1. **Solver diagnostics.** Log iteration count, constraint violation, cost components per solve. Spike alerts on regressions.
2. **Simulation regression set.** A fixed library of scenarios (nominal, edge, adversarial) replayed on every code change. Track success rate, peak constraint violation, runtime.
3. **Hardware-in-the-loop in a safe enclosure.** Reduced speed, monitored e-stop, light curtain.
4. **Failure-mode list.** Document what happens for: infeasible, max-iter, NaN, tracking-error threshold breach, sensor dropout. Each one must have an explicit handler.

## Inputs

- **System dynamics description.** Class (kinematic / second-order / multibody-with-contact), state/control dims, actuator limits.
- **Task spec.** Start, goal (or goal set), waypoints, contact phases if any, horizon.
- **Constraints.** Joint, velocity, torque, friction, clearance, posture.
- **Real-time budget.** Offline / batch / online MPC rate.

## Outputs

A markdown design doc with:

1. Chosen formulation (collocation / shooting / DDP) with one-paragraph justification.
2. Decision variables, knot count, horizon.
3. Full cost function with weighted terms and scaling guidance.
4. Constraint list with hard/soft categorization.
5. Initialization strategy.
6. Solver and library recommendation with license.
7. Post-processing pipeline (resampling, retiming, runtime guards).
8. Real-time / offline decision and fallback policy.
9. Validation checklist.

## Examples

> "Design a trajectory optimization for a 7-DoF arm pouring a glass of water without spilling — minimize jerk, keep liquid surface near-horizontal."

Expected sketch:

- **Formulation:** direct collocation with 60 knots over 4 s.
- **Cost:** jerk squared (primary), end-effector orientation deviation from nominal pouring axis (high weight at all interior knots), joint-limit margin, posture bias toward elbow-up.
- **Constraints:** end-effector position equality at 5 waypoints (above glass, tilt-start, peak, retract, home), joint limits hard, velocity hard, torque hard, table-collision hard.
- **Init:** workspace straight-line through waypoints + IK; if that fails, warm-start from a short RRT-Connect path.
- **Solver:** Drake direct collocation with IPOPT-class NLP backend.
- **Post:** Ruckig retime; runtime tracking error guard at 5 mm Cartesian.
- **Validation:** 30 simulated pour scenarios across glass heights, then a caged hardware soak at 50% speed before any human-adjacent test.

## Limitations

- This skill does not pick numerical weights for cost terms beyond providing a scaling rule. Final tuning is task-specific.
- Contact-implicit formulations are mentioned but not deeply specified; they are an active research area and need expert review.
- Learning-based warm-starts (diffusion policies, neural MPC) are out of scope.
- Recommendations assume rigid-body dynamics. Soft-body, fluid coupling, and granular interaction need specialized formulations.
- Re-verify licenses of any vendored library before shipping.

## Source references (URL-only)

- https://github.com/loco-3d/crocoddyl
- https://github.com/RobotLocomotion/drake
- https://github.com/moveit/moveit2
- https://github.com/ompl/ompl
- https://github.com/stack-of-tasks/pinocchio
- https://github.com/flexible-collision-library/fcl
