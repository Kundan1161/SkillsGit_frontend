# Synthesis Report — Robotics: ROS 2 Architecture

**Wave:** 3
**Niche:** robotics — ROS / ROS 2 architecture (nodes, lifecycle, QoS, message design, navigation stack)
**Author agent:** Wave-3 methodology-synthesis agent
**Date:** 2026-05-14

## Skills produced

All four are net-new (no prior overlap in `synth/`). All have `license_type: free`, the mandatory robotics safety disclaimer in `## When to use`, body length 300-700 lines, frontmatter compliant with `prompts/shared/skills-md-spec.md`.

1. `synth/ros2-system-architecture-reviewer.skills.md` — version 1.0.0
   Audit a ROS 2 robot stack: node graph, composition, lifecycle, executors, QoS per topic, message-schema design, parameters, launch and test isolation, DDS/discovery, clocks, observability. 12 stages, ~400 body lines.

2. `synth/ros2-behavior-tree-designer.skills.md` — version 1.0.0
   Design a behavior tree for an autonomous task. Mission decomposition, skill inventory, control-flow vocabulary, recovery sub-tree design with budgets and commit-point handling, blackboard discipline, ticking strategy, ROS 2 integration, testing. 10 stages.

3. `synth/ros2-navigation-stack-tuner.skills.md` — version 1.0.0
   Tune Nav2 for a target environment. Footprint and kinematics, costmap common params, layered costmaps, planner choice (NavFn, SMAC family, Theta*), controller choice (DWB, RPP, MPPI), behavior server, smoothing, BT integration, observability, symptom-driven adjustments, verification checklist. 12 stages.

4. `synth/ros1-to-ros2-migration-planner.skills.md` — version 1.0.0
   Plan a ROS 1 → ROS 2 migration. Inventory and triage, distribution choice, interface mapping (topics/services/actions/dynamic_reconfigure/nodelets), lifecycle and composition redesign, ros1_bridge strategy with sunset, parameter and launch migration, rosbag and tooling, testing, risk register, phased rollout. 12 stages.

The fifth optional skill (robot-message-schema-designer) was scoped but not produced — the architecture-reviewer's Stage 6 already covers message-design review at a useful depth, and a standalone schema-designer would risk duplication without a clearly different use case. The architecture-reviewer can be augmented later if demand surfaces.

## Sources reviewed (all license-verified)

License verification was performed by direct WebFetch of each repo's GitHub page and, where ambiguous, the LICENSE file or package.xml. All cited sources are MIT, Apache-2.0, or BSD-3-Clause — eligible per the synth rules.

- https://github.com/ros2/ros2 — Apache-2.0 (ROS 2 meta repository)
- https://github.com/ros2/rclcpp — Apache-2.0 (C++ client library)
- https://github.com/ros2/rmw — Apache-2.0 (middleware interface)
- https://github.com/ros2/design — Apache-2.0 (design documentation)
- https://github.com/ros2/launch — Apache-2.0 (launch system)
- https://github.com/ros2/common_interfaces — Apache-2.0 (standard messages; verified via package.xml)
- https://github.com/ros2/demos — Apache-2.0 (example code)
- https://github.com/ros-controls/ros2_control — Apache-2.0 (hardware abstraction)
- https://github.com/ros-navigation/navigation2 — Apache-2.0 default with some BSD-3-Clause and a small LGPL-2.1 footprint; cited at the Apache-2.0-default scope only
- https://github.com/moveit/moveit2 — BSD-3-Clause (motion planning, referenced in migration planner)
- https://github.com/BehaviorTree/BehaviorTree.CPP — MIT (behavior-tree library)
- https://github.com/micro-ROS/micro_ros_setup — Apache-2.0 (microcontroller ROS)

## License rejections

- **Foxglove Studio** — Mozilla Public License (MPL). Rejected per synth rules (MIT/Apache/BSD/ISC/Unlicense only). Not cited.
- **Some Navigation2 packages** are LGPL-2.1-or-later. The Nav2 repo is cited under its default Apache-2.0 license; LGPL-licensed sub-packages were not directly relied on.

## Methodology patterns surfaced

Cross-cutting patterns identified during synthesis and reflected in the skills:

- **QoS as a per-topic design decision, not a default**. Sensor data → BEST_EFFORT/VOLATILE; commands → RELIABLE/VOLATILE; latched state (robot_description, map) → RELIABLE/TRANSIENT_LOCAL. Mismatches are silent-failure landmines.
- **Composition + intra-process for high-rate paths**, separate processes for fault isolation. The two pressures must be balanced deliberately.
- **Executor and callback-group correctness as a deadlock surface**. Synchronous service calls from single-threaded executors are textbook deadlocks; the architecture-reviewer flags this as a Major.
- **Lifecycle for safety-critical and resource-owning nodes**. Resource allocation in `on_configure`, resource start in `on_activate`, and `on_deactivate` must actually stop effect.
- **Recovery design at the right scope** in behavior trees — local/mid/high-level recovery with explicit budgets, named reusable sub-trees, and commit-point handling.
- **Costmap layer ordering and inflation tuning** as the most common source of Nav2 frustration. Symptoms map to specific parameter levers.
- **Bridge-with-sunset** as the only credible phased ROS 1 → ROS 2 migration shape for live fleets.
- **Frame, units, and timestamp discipline** on every spatial or temporal message — encode units in field names; populate `Header.frame_id` and `stamp` from the source clock, not `now()`.

## Confidence

High on:
- Architecture review methodology — the QoS taxonomy, executor pitfalls, composition trade-offs, and lifecycle patterns are well-attested across the cited Apache-2.0 design docs and reference implementations.
- Behavior-tree design vocabulary — BehaviorTree.CPP and Nav2's BT idioms converge on the same control-node set and recovery patterns.
- Nav2 tuning structure — the costmap-layer / planner / controller / behavior-server decomposition is canonical; specific parameter values are starting points, called out explicitly in each skill's Limitations.
- Migration phasing shape — the bridge-with-sunset pattern is broadly applicable; precise effort estimates are not, and the migration planner explicitly says so.

Medium on:
- Specific parameter starting values in the Nav2 tuner. These reflect commonly-recommended ranges and are flagged as starting points to validate empirically. The skill's Stage 11 (verification checklist) is the safety net.
- MPPI tuning depth in the Nav2 skill. MPPI is newer and the synth reflects the surface-level controller-selection criteria rather than deep critic tuning. A future version could deepen this section.

Lower on:
- micro-ROS specifics. The architecture-reviewer mentions micro-ROS in the platform-target dropdown and acknowledges the bridge to companion computers, but a dedicated micro-ROS skill would deepen coverage for embedded targets. Candidate follow-up.

## Mandatory safety disclaimer

All four skills include the exact required disclaimer block in their `## When to use` section:

> This skill produces methodology guidance for robot software architecture. Outputs must be reviewed by qualified robotics engineers and validated in simulation and bench tests before any deployment on hardware that interacts with people or property. Bad robot software causes physical harm — treat all advice as a starting point, not a deployment-ready specification.

Each skill also closes with a `## Limitations` section that reinforces sim-then-bench-then-field validation and human supervision.

## Tagging

All skills carry `category: robotics` and `niche:ros2-architecture` as the first tag, with 4-7 additional tags each covering the more specific subdomain (qos, lifecycle, behavior-tree, costmap, planner, migration, etc.).

## Follow-up candidates (not produced this wave)

1. `robot-message-schema-designer` — a standalone deep dive on message/service/action schema design with versioning, units, frames, and latency budgets. Scoped but folded into Stage 6 of the architecture-reviewer this wave; could split out if a single-purpose skill is wanted.
2. `micro-ros-companion-architecture` — micro-ROS on MCU paired with a companion computer; QoS, agent topology, bandwidth budgeting, partial-failure modes.
3. `ros2-fleet-management-architecture` — multi-robot ROS 2 systems (namespacing, discovery server, central manager, observability across robots).
4. `moveit2-pipeline-tuner` — analogous to the Nav2 tuner but for manipulator motion planning (planner choice, OMPL parameters, collision checking, time parameterization).
5. `ros2-real-time-readiness-audit` — focused review for hard-real-time ROS 2 deployments (PREEMPT_RT, executor choice, allocator strategy, timing analysis).
6. `gazebo-or-gz-sim-test-harness-designer` — design a simulation test harness for a ROS 2 stack with deterministic seeding, sensor noise injection, and CI integration.

## Validation status

The four skills have been written against the spec in `prompts/shared/skills-md-spec.md`. They have not been run through `apps/api/src/skills/validator.py` (that is the integration step described in `synth/README.md`). Frontmatter fields, body section headers (`## When to use`, `## How to apply`, plus recommended sections), and the platform-curated authoring conventions all conform to the spec as read.
