---
id: skillsgit-curated/motion-planner-selector
version: 1.0.0
name: Motion Planner Selector
description: Recommend a motion-planning family (sampling, optimization, search, hybrid) and collision-checking strategy for a given robot, environment, and task.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-robotics
    role: author
category: robotics
tags:
  - niche:motion-planning
  - planner-selection
  - rrt
  - prm
  - chomp
  - collision-checking
  - manipulation
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
  - motion planner
  - path planning
  - rrt
  - rrt*
  - prm
  - chomp
  - trajopt
  - ompl
  - moveit
  - collision checking
  - manipulation planning
example_invocations:
  - "Recommend a planner for a 7-DoF arm doing pick-and-place in cluttered shelves."
  - "I have a mobile base with a 2D LiDAR map. Which planner family?"
  - "Our planner times out on narrow-passage problems — what should we switch to?"
  - "How should we set up collision checking for a humanoid in a kitchen?"
inputs:
  - name: robot_description
    type: text
    required: true
    description: Robot kinematic class (mobile base, 6/7-DoF arm, humanoid, dual-arm, aerial), DoF count, joint limits and self-collision constraints.
  - name: environment_description
    type: text
    required: true
    description: Static vs dynamic obstacles, narrow passages, known map vs partial observability, cluttered or open.
  - name: task_constraints
    type: text
    required: true
    description: Task type (free-space, contact-rich, grasping, navigation), real-time budget, smoothness/jerk constraints, kinodynamic constraints.
  - name: existing_stack
    type: text
    required: false
    description: Existing software stack (ROS/ROS 2, MoveIt, custom), preferred languages, hardware (CPU/GPU).
outputs:
  - name: planner_recommendation
    type: markdown
    description: A ranked recommendation with primary planner family, fallback, collision-check strategy, and integration sketch.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Motion Planner Selector

## When to use

Use this skill when a roboticist needs to decide **which family of motion planner** to deploy for a specific robot, environment, and task — for example:

- A 7-DoF manipulator doing pick-and-place in a cluttered shelf.
- A mobile base navigating an indoor map with moving people.
- A dual-arm robot performing coordinated assembly with contact constraints.
- A flying platform with kinodynamic constraints.
- An existing planner that fails on narrow passages, times out, or produces jerky motion.

The skill does **not** write a planner from scratch. It maps task characteristics to a planner family (sampling-based, optimization-based, search-based, or hybrid), recommends a collision-checking strategy, and points to a small set of permissively licensed reference implementations.

**Safety disclaimer (mandatory):** This skill produces methodology guidance. Robot motion-planning failures cause physical harm. Every recommendation must be reviewed by qualified roboticists, validated in simulation, and bench-tested in a safe enclosure before any deployment near people or valuable property. Treat all advice as a starting point — never deployment-ready.

## How to apply

Run through the seven steps below in order. Do not skip the decision matrix; the wrong planner family is the most common cause of motion-planning failure.

### Step 1 — Characterize the configuration space

Establish the *shape* of the search problem before naming any algorithm.

- **Dimensionality.** Count actuated DoF. <= 3 favors grid/search; 4–8 is the sweet spot for sampling-based methods; >12 strongly favors optimization-based methods or learned policies.
- **Topology.** Is the C-space a Cartesian product of revolute and prismatic joints? Are there closed kinematic chains (dual-arm grasping the same object, parallel mechanisms)? Closed chains require constraint-based or projection-based planners.
- **Differential constraints.** Does the system have non-holonomic constraints (car-like base) or full second-order dynamics (quadrotor, legged robot)? If yes, you need a kinodynamic or trajectory-optimization formulation, not pure geometric planning.
- **Goal type.** Single goal pose, goal region, task-space goal (e.g., any grasp on a handle), or a sequence of waypoints?

Record these four answers; they drive every downstream choice.

### Step 2 — Characterize the environment

- **Static vs dynamic.** Static environments support precomputed roadmaps (PRM, lattice). Dynamic environments need replanning (RRT-Connect, lazy PRM, anytime A*, MPC).
- **Observability.** Fully known map vs partial (planning under occlusion). Partial observability pushes toward receding-horizon planning.
- **Narrow passages.** If task-relevant volumes have aspect ratio worse than ~1:50, uniform sampling will struggle. Plan for bridge-sampling, RRT-Connect with workspace guidance, or hybrid optimization warm-starts.
- **Clutter density.** High clutter favors lazy collision checking (defer expensive checks until a candidate path is found).

### Step 3 — Characterize the task budget

- **Real-time budget per query.** <10 ms = reactive control loop (use MPC or precomputed lattice). 10–500 ms = anytime sampling planner. >500 ms = full optimization or multi-query roadmap.
- **Offline vs online.** Offline single-shot allows expensive smoothing and global optimization. Online replanning needs warm-startable, anytime algorithms.
- **Optimality requirements.** "Any feasible path" -> RRT, RRT-Connect. "Asymptotically optimal" -> RRT*, PRM*, BIT*, AIT*. "Locally optimal smooth" -> CHOMP, STOMP, TrajOpt.
- **Smoothness/jerk constraints.** Sampling-based outputs are jagged and require post-smoothing. Optimization-based outputs are smooth by construction but may be infeasible if initialization is bad.

### Step 4 — Use the decision matrix

| Scenario | Primary family | Specific algorithms | Fallback |
|---|---|---|---|
| Low DoF (<= 3) mobile base, known map | Search-based | A*, D* Lite, Hybrid A* (car-like) | Sampling-based RRT-Connect |
| 6–8 DoF arm, free-space pick-place, clutter | Sampling-based (asym. optimal) | RRT-Connect for feasibility; BIT*/AIT* for optimality | Hybrid: sampling + post-smoothing |
| 7+ DoF arm, smooth contact-rich task | Optimization-based | CHOMP, STOMP, TrajOpt | Sampling warm-start, then optimize |
| Narrow passage, low-clearance task | Hybrid | RRT-Connect + workspace guidance, then TrajOpt smoothing | Bridge-sampled PRM |
| Dual-arm closed-chain | Constraint-based sampling | CBiRRT, Atlas-RRT | Constrained optimization |
| Kinodynamic (car, quadrotor) | Kinodynamic sampling | KPIECE, SST, kinodynamic RRT | Lattice + optimization |
| High-DoF humanoid whole-body | Optimization | Differential dynamic programming (DDP), iLQR, MPC | Hierarchical: footstep search + body optimization |
| Reactive obstacle avoidance | MPC / local planner | DWA, TEB, MPPI | Velocity obstacles |

If a row matches more than one of your characteristics, prefer the **simpler** family and add hybrid post-processing only if the simpler family fails benchmarks.

### Step 5 — Choose a collision-checking strategy

Collision checking typically consumes 70–95% of planner time. The strategy must match the planner:

- **Broad-phase + narrow-phase.** Always start here. Broad-phase (AABB/BVH, sweep-and-prune) rejects far-away pairs cheaply. Narrow-phase (GJK/EPA, mesh-mesh) runs only on candidate pairs.
- **Discrete vs continuous (CCD).** Discrete checks at samples along edges miss tunneling for fast motions or thin obstacles. Use CCD (continuous collision detection) for high-speed paths, thin walls, or safety-critical clearances. Sampling-based planners commonly use discrete with adaptive subdivision; optimization-based planners use signed distance fields (SDFs) which are inherently continuous.
- **Lazy vs eager.** Lazy: build the roadmap/tree first, check collisions only on the candidate path. Eager: check every edge as it's added. Lazy wins in cluttered scenes where most edges never get used.
- **Conservative checking.** Inflate robot bodies by a safety margin equal to (max joint velocity * controller cycle time) + sensor noise. Never use the nominal mesh in production.
- **Acceleration structures.** For fixed scenes, precompute BVH/k-d trees. For deformable or articulated obstacles, rebuild per cycle.
- **GPU acceleration.** Worth the engineering cost only when you are doing >100k checks/sec or batch planning many alternatives (e.g., Monte Carlo rollouts, learned policies). Otherwise CPU FCL is fine.

### Step 6 — Pick a reference implementation

Use one of these permissively licensed projects as a starting point. Read their licenses yourself before vendoring code.

- **OMPL** (BSD-3-Clause) — sampling-based planners (RRT family, PRM family, BIT*, AIT*, KPIECE, SST). The reference library for geometric and kinodynamic sampling.
- **MoveIt 2** (BSD-3-Clause) — full manipulation stack on top of OMPL, with pre-wired collision checking, scene management, and ROS 2 integration.
- **Drake** (BSD-3-Clause) — multibody dynamics, trajectory optimization (TrajOpt-style), MPC, and IK. Strong for optimization-based approaches.
- **AIKIDO** (BSD-3-Clause) — constrained motion planning and trajectory execution.
- **FCL** (BSD) — broad-phase and narrow-phase collision checking; used by MoveIt and many others.
- **Open3D** (MIT) — point-cloud and mesh utilities, useful for building collision scenes from perception.
- **Nav2** (Apache-2.0 default — check per-package; some packages are LGPL) — ROS 2 mobile-base navigation stack.

If your stack is ROS 2-based, MoveIt 2 + OMPL + FCL is the default. If you need optimization-heavy whole-body control, Drake is the default. Mix only when you have a reason.

### Step 7 — Define the validation plan

Before deploying, the user must commit to a validation chain. Refuse to give a "final" recommendation until they confirm:

1. **Unit benchmarks.** Run the chosen planner against a benchmark set (e.g., MotionBenchMaker, OMPL benchmark scripts) for the robot/scene. Capture success rate, time-to-first-solution, path cost.
2. **Simulation regression.** Run in Gazebo / Drake / MuJoCo with realistic friction, latency, and sensor noise. Stress-test with adversarial scenes.
3. **Hardware-in-the-loop in a safe enclosure.** Cage, light curtains, reduced speed, monitored e-stop. Repeat the simulation regression set on hardware.
4. **Failure-mode analysis.** What does the planner do when it returns infeasible? When it times out? When the goal is unreachable? Every failure mode must have a defined fallback (replan, slow down, halt, alert human).

## Inputs

- **Robot description.** DoF, kinematic class, joint limits, dynamic limits, self-collision links.
- **Environment description.** Static/dynamic, observability, clutter, narrow passages, task volume aspect ratio.
- **Task constraints.** Real-time budget, optimality requirements, smoothness, kinodynamic constraints, goal type.
- **Existing stack (optional).** ROS/ROS 2 version, languages, hardware budget.

## Outputs

A markdown report with:

1. A one-paragraph summary of the recommended planner family and why.
2. A "primary + fallback" pair (e.g., "Primary: RRT-Connect with shortcut smoothing; Fallback: TrajOpt warm-started from the RRT-Connect path").
3. A collision-checking strategy block (broad/narrow phase, discrete vs CCD, lazy vs eager, safety margin formula).
4. A specific reference implementation suggestion with the license noted.
5. A validation checklist tailored to the use case.
6. A list of known failure modes for the recommended family and how to detect them at runtime.

## Examples

> "Recommend a planner for a Franka Panda doing bin-picking from a cluttered tote, replanning at 2 Hz, with safety mats."

Expected output sketch:

- **Primary:** RRT-Connect in OMPL via MoveIt 2 with lazy FCL collision checking. Asymptotic optimality is not required at 2 Hz; feasibility-first is correct.
- **Smoothing:** Shortcut + parabolic time-parameterization. Optional: TrajOpt post-pass if jerk limits are tight.
- **Collision:** FCL broad-phase BVH over the static scene plus per-frame point-cloud voxel grid from the wrist camera, inflated by 1.5 cm.
- **Validation:** Run on MotionBenchMaker bookshelf benchmark, then 200 simulated bin scenes with randomized clutter, then a caged hardware soak at 25% speed.

## Limitations

- This skill does not pick **specific hyperparameters** (sample density, RRT goal-bias, CHOMP step size). Those are tuned per-deployment.
- It does not cover learned planners (RL, diffusion, learned heuristics). Those require their own evaluation framework and are out of scope.
- Recommendations assume rigid-body robots. Soft robots, cable-driven systems, and granular-media interaction need specialized methods.
- The collision-check guidance assumes mesh-based geometry. If you only have implicit (SDF, NeRF) representations, the broad/narrow distinction changes.
- License notes are point-in-time. Re-verify the license of any vendored library before shipping.

## Source references (URL-only)

- https://github.com/ompl/ompl
- https://github.com/moveit/moveit2
- https://github.com/RobotLocomotion/drake
- https://github.com/personalrobotics/aikido
- https://github.com/flexible-collision-library/fcl
- https://github.com/ros-navigation/navigation2
- https://github.com/isl-org/Open3D
