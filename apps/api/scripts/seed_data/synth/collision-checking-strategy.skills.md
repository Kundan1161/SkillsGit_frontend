---
id: skillsgit-curated/collision-checking-strategy
version: 1.0.0
name: Collision Checking Strategy
description: Choose collision-checking layers — broad-phase, narrow-phase, discrete vs CCD, conservative margins, GPU acceleration, and real-time simplifications.
authors:
  - name: Wave-3 Methodology Synthesis
    handle: wave3-robotics
    role: author
category: robotics
tags:
  - niche:motion-planning
  - collision-checking
  - fcl
  - bvh
  - ccd
  - sdf
  - real-time
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
    - gemini-1.5-pro
  min_context_tokens: 24000
  tools_optional:
    - web_search
  estimated_tokens_per_invocation: 5500
trigger_keywords:
  - collision checking
  - collision detection
  - fcl
  - ccd
  - swept volume
  - bvh
  - signed distance field
  - sdf
  - self-collision
example_invocations:
  - "Set up collision checking for a 7-DoF arm with a wrist-mounted depth camera."
  - "Our planner tunnels through thin walls — what should we change?"
  - "Do we need GPU collision checking for 10k Monte Carlo rollouts?"
  - "Recommend safety margins for a 1 m/s mobile base."
inputs:
  - name: scene
    type: text
    required: true
    description: Static vs dynamic, geometry source (CAD meshes, point clouds, voxel grids, SDFs), update rate, expected obstacle count.
  - name: robot_geometry
    type: text
    required: true
    description: Robot link meshes (high-poly CAD or simplified primitives), self-collision link pairs, attached payloads.
  - name: motion_profile
    type: text
    required: true
    description: Max link speeds and accelerations, controller cycle time, sensor noise envelope.
  - name: planner_context
    type: text
    required: false
    description: Which planner consumes the checks (sampling, optimization, MPC) and the query rate budget.
outputs:
  - name: collision_strategy
    type: markdown
    description: A layered collision-checking design with broad/narrow choice, discrete vs CCD policy, safety-margin formula, acceleration structure plan, and validation harness.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Collision Checking Strategy

## When to use

Use this skill when a roboticist needs to **design or repair the collision-checking layer** that a motion planner, MPC controller, or safety monitor relies on. Typical triggers:

- A planner that takes too long because every edge runs an expensive mesh-mesh check.
- Paths that "tunnel" through thin walls or fast-moving obstacles because checks are discrete.
- Self-collisions that the system did not catch in simulation.
- A move from CAD meshes to point-cloud-driven scenes (or vice versa) where the prior strategy no longer works.
- A decision on whether GPU collision checking is worth the engineering effort.

This skill does **not** implement collision detection. It maps the scene, robot, and motion profile to a layered strategy and recommends permissively licensed reference libraries.

**Safety disclaimer (mandatory):** This skill produces methodology guidance. Robot motion-planning failures cause physical harm. A missed collision check can break the robot, the workspace, or a person. Every recommendation must be reviewed by qualified roboticists, validated in simulation, and bench-tested in a safe enclosure before any deployment near people or valuable property. Treat all advice as a starting point — never deployment-ready.

## How to apply

Work the steps in order. Collision checking is one of those subsystems where the *combination* of choices matters more than any single choice.

### Step 1 — Inventory geometry sources

Catalogue every geometry source the system will check against:

- **Robot self.** Per-link mesh (high-poly CAD vs simplified primitives), attached payloads (gripper, tool, grasped object).
- **Static scene.** CAD model, surveyed mesh, occupancy grid, SDF.
- **Dynamic scene.** Sensor stream (point cloud, depth image, occupancy grid update), tracked-object boxes.
- **Other agents.** Other robots in the cell, humans (often modeled as inflated capsules).

For each source, record (a) update rate, (b) noise / latency envelope, (c) representation. Mixing representations is fine but every layer of the strategy must know what it is checking against.

### Step 2 — Simplify robot geometry

High-poly CAD meshes are wrong for collision checking. They are too detailed (slow narrow-phase) and often over-tight (missed clearances). Build a **collision proxy**:

- Wrap each link in convex hulls or a small set of capsules / cylinders / boxes.
- Keep the visual mesh separate; never use the visual mesh for checks.
- Inflate each proxy by a fixed buffer (Step 5).
- Mark self-collision-allowed pairs (adjacent links that physically overlap by design) so the checker doesn't flag them.

This step alone is often a 5–20x speedup over raw-CAD checking and is the single biggest engineering win.

### Step 3 — Broad-phase + narrow-phase architecture

Always build collision checking as two layers:

- **Broad-phase.** Cheap, conservative, rejects pairs that cannot possibly be in contact.
  - Sweep-and-prune on axis-aligned bounding boxes (AABBs).
  - Bounding volume hierarchies (BVH) over static scene meshes.
  - Spatial hashing for many small dynamic objects.
- **Narrow-phase.** Expensive, exact, runs only on candidate pairs from broad-phase.
  - GJK + EPA for convex-convex distance.
  - Mesh-mesh via BVH descent.
  - SDF lookups when the static scene is represented as an SDF.

The right rule of thumb: broad-phase should reject >99% of pairs.

### Step 4 — Discrete vs continuous (CCD)

A discrete check tests "is the robot in collision at this configuration?". A continuous check tests "does the robot collide anywhere along this motion?".

- **Discrete with adaptive subdivision.** Default for sampling-based planners. Subdivide edges until consecutive samples are within a safe step in C-space (smaller than the smallest obstacle feature divided by 2).
- **Continuous (CCD).** Required when (a) the smallest obstacle feature is comparable to a typical edge length, (b) motions are fast relative to the controller cycle, or (c) you have hard safety constraints around thin or sharp obstacles.
- **Signed distance fields.** SDFs give continuous gradients useful for optimization-based planners (CHOMP, TrajOpt) and avoid the tunneling problem for free. Cost: SDF construction is expensive, and only practical for largely-static scenes.

**Tunneling diagnostic.** If your planner ever produces paths that look fine in simulation but penetrate obstacles when re-checked at fine resolution, you have a tunneling bug. Subdivide more aggressively or switch to CCD/SDF.

### Step 5 — Safety margins

The collision check should never use the nominal robot mesh. Inflate by a safety margin that accounts for:

- **Tracking error.** Maximum expected position error between commanded and actual robot state. Get this from the controller team or measure it.
- **Sensor noise.** Worst-case sensor error envelope for dynamic obstacles.
- **Latency.** (Max link velocity) × (perception-to-actuation latency). If you replan at 10 Hz on a 1 m/s mobile base, you need at least 10 cm of margin just for latency.
- **Model error.** CAD vs as-built tolerance.

Combine conservatively: `margin = tracking_error + sensor_noise + v_max * latency + model_error`. Treat this as a floor; pad further for human proximity.

For high-DoF arms, set a tighter margin near the end-effector (where task precision matters) and a looser margin on proximal links (where collisions are catastrophic but rare).

### Step 6 — Acceleration structures and update policy

- **Static-scene BVH.** Build once at scene load. FCL handles this; verify the BVH refits on any scene edit.
- **Dynamic-object refitting.** Refit AABBs each cycle for objects that moved. Avoid full rebuilds.
- **Point-cloud voxelization.** For wrist-camera streams, voxelize and inflate before checking. Treat each voxel as a small static obstacle for the planner's horizon.
- **SDF tile updates.** If you maintain an SDF, update only the tiles touched by perception this cycle; keep the rest stable.
- **Caching.** Many planners re-check the same edges across iterations. A small LRU cache keyed on (config_a, config_b) often cuts checks by 30–60%.

### Step 7 — Lazy vs eager evaluation

- **Eager.** Check every candidate as it is generated. Simple, slow.
- **Lazy.** Defer checks until you have a candidate path; check the path in coarse-to-fine order and bail at the first failure. Re-plan around the failure. Lazy wins in cluttered scenes where most candidate edges are never used.
- **Hybrid.** Eager broad-phase (fast), lazy narrow-phase (slow). Default for most modern stacks.

Match this to the planner: sampling-based planners benefit most from lazy narrow-phase. Optimization-based planners need gradients, so they tend to use eager SDF queries each iteration.

### Step 8 — Decide on GPU acceleration

GPU collision checking is glamorous and often unnecessary. Use it when:

- You are running >10⁵ checks/sec (batch planners, learned policies with rollouts, RL training).
- You are doing Monte Carlo planning or sampling many alternative trajectories simultaneously.
- You have a GPU-resident perception pipeline already and the data is local.

Skip it when:

- You are doing single-arm pick-place planning at human rates. A well-tuned CPU stack (FCL + good broad-phase) is enough.
- Your bottleneck is somewhere else (planner search, IK, communication). Measure first.

Most production manipulation stacks run CPU collision checking. Most large-scale RL training pipelines run GPU.

### Step 9 — Pick reference implementations

- **FCL** (BSD) — the de facto reference for broad/narrow-phase collision detection on meshes and primitives. Used by MoveIt 2.
- **MoveIt 2** (BSD-3-Clause) — integrates FCL, manages the planning scene, and handles attached objects.
- **Drake** (BSD-3-Clause) — multibody collision and contact queries, with strong SDF and signed-distance support for optimization-based planners.
- **Open3D** (MIT) — point-cloud and mesh processing for building collision proxies from perception.
- **Pinocchio** (BSD-2-Clause) — efficient rigid-body kinematics; pairs naturally with collision libraries for fast forward-kinematics + checking.

Re-verify the license of any library before vendoring.

### Step 10 — Validation plan

Refuse to call the design done until the user commits to:

1. **Unit tests.** Synthetic scenes with known-correct answers for every check type (separation, touching, penetration, swept-volume).
2. **Tunneling tests.** A fast motion through a thin wall; the checker must catch it.
3. **Self-collision tests.** Forced self-collision configurations; the checker must catch them, and the whitelist of allowed-collision pairs must be auditable.
4. **Margin regression.** Run with progressively smaller margins to find the smallest margin that still passes the test suite. Deploy with at least 2x that margin.
5. **Real-time profiling.** Worst-case wall-clock per check on the production hardware. The 99th percentile, not the mean.
6. **Hardware soak in a safe enclosure.** Reduced speed, light curtain, monitored e-stop, long-duration run that exercises many configurations.

## Inputs

- **Scene.** Static / dynamic split, geometry source, update rate, obstacle count.
- **Robot geometry.** Visual vs collision meshes; self-collision link pairs; attached payloads.
- **Motion profile.** Max speeds, accelerations, controller cycle time, sensor noise.
- **Planner context (optional).** Which planner consumes the checks and at what rate.

## Outputs

A markdown strategy doc with:

1. Geometry inventory (per source: representation, update rate, latency, noise).
2. Robot collision proxy plan.
3. Broad-phase + narrow-phase architecture choice with library.
4. Discrete vs CCD policy with reasoning.
5. Safety-margin formula with numeric values for the specific platform.
6. Acceleration-structure update policy.
7. Lazy vs eager evaluation choice.
8. GPU decision with justification.
9. Reference implementation recommendations with licenses.
10. Validation harness.

## Examples

> "A Franka Panda with a wrist depth camera, bin-picking in a cluttered tote at human-safe speeds. ROS 2 stack."

Expected sketch:

- **Proxy:** Per-link capsules + gripper convex hull. Inflate proxies by 1.5 cm.
- **Broad-phase:** FCL sweep-and-prune over static scene BVH plus per-frame voxel grid from the depth camera (2 cm voxels, dilated by 1 voxel).
- **Narrow-phase:** GJK on capsules vs voxels (cheap); mesh-mesh only on the gripper-vs-tote pair.
- **Continuous:** Discrete checks at C-space step <= 5 degrees per joint; subdivide further when minimum-distance < 2 cm.
- **Margin:** 1.5 cm proxy inflation + 1.0 cm tracking error + 0.5 cm sensor noise + 1.0 cm latency margin (at 100 ms perception-to-actuation, 100 mm/s peak) = 4 cm total minimum clearance.
- **Lazy/eager:** Eager broad-phase, lazy narrow-phase on candidate paths.
- **GPU:** Not needed at this scale.
- **Validation:** Tunneling test through a 3 cm vertical bar, 50 cluttered tote scenes, 4-hour caged hardware soak at 25% speed.

## Limitations

- This skill does not specify how to author collision meshes from CAD; assume a separate authoring step.
- Deformable-object collision (cloth, cables, soft grippers) is out of scope and needs specialized methods.
- Human modeling for safety beyond capsule inflation is out of scope; functional safety (ISO 10218, ISO/TS 15066) requires certified hardware and process.
- The margin formula is a starting point. Final margins must be validated empirically and signed off by a qualified safety engineer for any human-adjacent deployment.
- Re-verify licenses of any vendored library before shipping.

## Source references (URL-only)

- https://github.com/flexible-collision-library/fcl
- https://github.com/moveit/moveit2
- https://github.com/RobotLocomotion/drake
- https://github.com/isl-org/Open3D
- https://github.com/stack-of-tasks/pinocchio
- https://github.com/ompl/ompl
