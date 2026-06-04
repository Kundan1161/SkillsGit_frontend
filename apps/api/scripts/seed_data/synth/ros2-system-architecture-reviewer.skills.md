---
id: skillsgit-curated/ros2-system-architecture-reviewer
version: 1.0.0
name: ROS 2 System Architecture Reviewer
description: Audit a ROS 2 robot software architecture — node graph, composition, lifecycle, executors, QoS choices, message schemas, parameters, launch and test isolation.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: robotics
tags: [niche:ros2-architecture, ros2, node-graph, qos, lifecycle, dds, executors, architecture-review]
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
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - ros2 architecture review
  - audit ros2 node graph
  - review my ros2 system
  - ros2 qos audit
  - lifecycle node review
  - ros2 composition review
  - executor choice
  - ros2 launch review
  - ros2 best practices audit
  - dds qos profile
  - ros message design review
  - robot software architecture review
example_invocations:
  - "Audit our ROS 2 system — twelve nodes across two machines, occasional dropped lidar frames, review the node graph and QoS choices."
  - "Review this ROS 2 stack before we move from sim to a real robot. Focus on lifecycle, executors, and parameter handling."
  - "We are merging two ROS 2 subsystems written by different teams. Audit the combined node graph and message interfaces."
inputs:
  - name: node_inventory
    type: text
    required: true
    description: A list (or rendered ros2 node list / ros2 topic list output) describing every node, the topics, services, and actions it publishes and subscribes to, and which executable / package each node lives in.
  - name: launch_files
    type: text
    required: false
    description: Launch files (Python, XML, or YAML) that compose the system. Include includes, remaps, parameter loads, and namespace assignments.
  - name: message_schemas
    type: text
    required: false
    description: Relevant .msg, .srv, .action files — particularly any custom interfaces. Helpful when the message design itself is suspect.
  - name: target_platform
    type: choice
    required: false
    description: Where the system runs. Influences QoS, executor, and middleware advice.
    choices: [single-soc-arm, multi-machine-lan, edge-plus-cloud, microcontroller-and-companion, simulation-only, mixed]
  - name: ros2_distro
    type: choice
    required: false
    description: ROS 2 distribution. Some defaults and feature availability vary.
    choices: [humble, iron, jazzy, rolling, foxy, other]
  - name: domain
    type: choice
    required: false
    description: Robot domain — biases the review toward common failure modes for that domain.
    choices: [mobile-ground, aerial, manipulator, mobile-manipulator, sensor-network, industrial, research-prototype, other]
outputs:
  - name: architecture_review
    type: markdown
    description: Triaged findings by severity with per-node and per-topic anchors, a node-graph health summary, a QoS-profile table per topic, and a prioritized rework list.
  - name: findings_json
    type: json
    description: Machine-readable findings list for ingestion by review bots, CI dashboards, or migration planners.
---

# ROS 2 System Architecture Reviewer

## When to use

Use this skill when a robotics team hands you a ROS 2 system and asks for a pre-deployment or pre-merge architecture audit. Triggers include: the team is about to move a stack from simulation to a real robot for the first time; a robot has shipped and is exhibiting intermittent drops, lag, or message-ordering bugs that smell like middleware misuse; two subsystems built by different teams are being merged into one robot and the combined node graph has never been reviewed; a code freeze is approaching and the team wants a second opinion on QoS choices, executor selection, and lifecycle boundaries; or a security or platform team is reviewing a fleet of robots for consistency.

The skill applies whether the target is a single SBC running everything in one process, a multi-machine ROS 2 system with DDS over a LAN, an edge-plus-cloud architecture with DDS bridges, or a microcontroller running micro-ROS speaking to a companion computer. The check is the same; platform nuance layers on top.

It does not apply to: live debugging of a single misbehaving node (that is a node-debugging task and needs logs and rosbags, not the node graph); algorithm choice for a specific subsystem (e.g. "should we use EKF or UKF for fusion" — that is a control-engineering question); or hardware bring-up (drivers, kernel, real-time tuning — those have their own playbooks).

**This skill produces methodology guidance for robot software architecture. Outputs must be reviewed by qualified robotics engineers and validated in simulation and bench tests before any deployment on hardware that interacts with people or property. Bad robot software causes physical harm — treat all advice as a starting point, not a deployment-ready specification.**

The bar the skill applies is "would this system survive a noisy network, a node crash, a sensor brownout, a slow planner, and a sim-to-real handoff without surprising the operator?"

## Inputs

| Input | Required | Purpose |
| --- | --- | --- |
| `node_inventory` | yes | The nodes and their pub/sub/service/action edges — the graph under review. |
| `launch_files` | no | How the graph is composed, namespaced, and parameterized. |
| `message_schemas` | no | Custom interfaces under review. |
| `target_platform` | no | Where the system runs — biases QoS, executor, and middleware advice. |
| `ros2_distro` | no | Distribution — affects defaults and feature availability. |
| `domain` | no | Robot domain — biases the weighting of common failure modes. |

## How to apply

The agent walks the architecture deterministically. Each stage produces structured findings; the final stages rank and render them.

### Stage 1 — Inventory the node graph

1. Parse the node inventory into a graph. For each node, record: package, executable, namespace, every published topic with its message type, every subscribed topic with its message type, every advertised service and action, every consumed service and action, every declared parameter, and any timers.
2. Identify the *connected components* of the graph. A robot stack with multiple disconnected components is suspicious — either there is an undocumented bridge, or there are dead nodes that no one talks to.
3. Identify *fan-in and fan-out hotspots*. A topic with more than five subscribers and any non-default QoS choice is a finding (every subscriber pays the QoS tax). A node with more than ten subscriptions is suspect — it has probably accreted responsibilities and should be split.
4. Identify *orphan publishers and dangling subscribers*. A publisher with no subscriber is a Minor (probably development residue, sometimes intentional for telemetry). A subscriber with no publisher is a Major in production (the node will silently never receive data and may not surface that as a fault).
5. Identify *naming inconsistencies*. Topics that mix snake_case and camelCase, namespaces that mix singular and plural, and topic names that include node names are smells. Topic names should describe the data, not the source.
6. Identify *custom message types*. Note every non-`std_msgs`, non-`sensor_msgs`, non-`geometry_msgs`, non-`nav_msgs` type and queue it for the schema-design review in Stage 6.
7. Identify *namespaces and remappings*. A robot system that does not use namespaces is one robot away from a collision when a second robot is added. Missing namespace strategy is a Major for any multi-robot-capable platform.
7a. Identify *implicit graph dependencies* — a node that publishes a heartbeat on `/diagnostics_agg` consumed by an operator UI, a node that reads `/clock`, a node that depends on `/tf_static` being populated before it ticks. These are easy to miss in a list of "what does each node publish and subscribe."
7b. Count *cycles* in the graph. A robust ROS 2 system has few directed cycles; cycles in command/state flow are sources of oscillation and recovery-loop pathology. Flag every cycle found and ask the team to confirm it is intentional.
7c. Tag every node with its *fault domain*. If this node crashes, what stops working? Build a small dependency table — drivers fault to actuators; planners fault to mission progress; perception faults to autonomy; observability faults to the operator's view but not to motion.

### Stage 2 — Process and composition layout

8. Determine which nodes are *composable nodes* (loaded into a component container) and which run as their own process. Composition into a single container avoids serialize/deserialize and copy costs across in-process boundaries — for high-rate sensor pipelines (lidar, camera, IMU at >50 Hz), nodes that are co-located on the same machine and pass large messages should be composable.
9. Flag *large-message inter-process publishers* that should be composed. A camera node publishing 1080p frames at 30 Hz into a separate-process subscriber on the same machine is a Major performance issue — recommend intra-process zero-copy via component composition.
10. Conversely, flag *over-composition*. Putting safety-critical and crash-prone experimental nodes in the same container means one segfault takes both down. Fault-isolation boundaries must be drawn deliberately.
11. Check whether *intra-process communication* is enabled in the composable container (`use_intra_process_comms=True`). Composition without intra-process comms gives up most of the win. Missing is a Major if any composed node passes large messages.
12. Identify *process boundaries that cross machines*. Any topic flowing across a machine boundary is a DDS-discovery and QoS concern. Mark these for Stage 4.
13. Check for *Python and C++ node mixing*. Mixed-language nodes in the same container are not supported; flag if seen. A mixed system is fine across processes, but performance-critical paths should prefer C++.
13a. Check the *executable density* per machine. Twenty processes on a 2-core SBC means twenty context-switching costs and twenty redundant DDS contexts. Composition is the lever; flag where the team has not used it.
13b. Check *memory budgets*. A composable container that loads three large model-bearing nodes (perception inference, motion planning, mapping) on a 4 GB device is one OOM event away from a crash. Flag and recommend either separation (so the OOM kills the noisy node alone) or a smaller payload (quantized models, streaming inference).

### Stage 3 — Executors and threading

14. For each composable container or multi-callback node, identify the *executor type* (`SingleThreadedExecutor`, `MultiThreadedExecutor`, `StaticSingleThreadedExecutor`, custom). The default single-threaded executor serializes every callback in that node — fine for simple nodes, fatal for a planner whose callback can be preempted by a service request.
15. Flag *single-threaded executors handling slow callbacks*. A planner callback that runs for 200 ms inside a single-threaded executor blocks every other callback in that container — the imu callback misses its deadline, the heartbeat fails, the safety stop is delayed. Recommend either a multi-threaded executor, a separate node, or moving the slow work to a worker thread.
16. Inspect *callback groups*. Mutually exclusive groups serialize their callbacks; reentrant groups run them in parallel. A reentrant group is required when a service callback can block on another service the same node provides (otherwise deadlock).
17. Flag *deadlock-prone patterns*. Calling a synchronous service from a single-threaded executor inside another callback of the same executor is a textbook deadlock — the service response can never be processed. Recommend the async API or a reentrant callback group on a multi-threaded executor.
18. Flag *unbounded thread pools*. A multi-threaded executor with no `num_threads` argument inherits a system default that can spawn enough threads to oversubscribe a small SBC. Set it deliberately to the number of CPU cores reserved for that container.
19. Note *callback priorities and CPU affinity*. Critical real-time work (control loops) should not contend with logging or visualization on the same core. Flag any system that does not pin time-critical executors.
19a. Check *timer drift handling*. A 100 Hz timer that takes 12 ms to fire on average is not running at 100 Hz; the executor is overloaded. Recommend instrumenting timer-callback duration and surfacing the actual rate as a diagnostic.
19b. Check *blocking sleeps inside callbacks*. `std::this_thread::sleep_for` inside a callback freezes the executor for that duration. Anything that needs delay should be a timer-driven follow-up, not a sleep.
19c. Check *async vs sync action client patterns*. The `send_goal` API on action clients has both shapes; in single-threaded contexts the async form is mandatory. Flag synchronous patterns inside non-reentrant contexts.

### Stage 4 — QoS profile choices

20. For every topic in the graph, the agent assigns a recommended QoS profile based on the data character. Compare to the declared profile (in code or launch files) and flag mismatches.
21. *Sensor data* (lidar scans, camera frames, IMU) should use the `sensor_data` profile or equivalent — `BEST_EFFORT` reliability, `VOLATILE` durability, small history depth. Using `RELIABLE` on a 30 Hz camera over Wi-Fi will silently buffer until OOM. Flag as Major.
22. *Commands* (velocity commands, joint commands, mode requests) should use `RELIABLE`, `VOLATILE`, small history. A dropped velocity command is a safety issue; a re-played stale velocity command is also a safety issue. Flag mismatches.
23. *Latched state* — robot description (URDF), map, static transforms — should use `RELIABLE`, `TRANSIENT_LOCAL`, depth 1. A late-joining subscriber must see the last value. Missing `TRANSIENT_LOCAL` on `/robot_description` or `/map` is a Major.
24. *Transforms* — `/tf` is `BEST_EFFORT`, `VOLATILE`, depth 100 by convention; `/tf_static` is `RELIABLE`, `TRANSIENT_LOCAL`, depth ~100. Deviations break every TF consumer in subtle ways.
25. *Diagnostics and heartbeats* should be `RELIABLE`, `VOLATILE`, depth small. A diagnostic that is `BEST_EFFORT` will mislead the operator when the network degrades — the diagnostic will silently fail to surface a problem.
26. *Liveliness* and *deadline* QoS policies are set only where the application needs them. Setting `LIVELINESS_AUTOMATIC` on every topic is a waste; setting `MANUAL_BY_TOPIC` requires the publisher to actually assert liveliness or every subscriber will fire dead-publisher events.
27. *History depth* matches the consumer pace. A subscriber that processes at 10 Hz with a depth-1 queue and a 100 Hz publisher will drop 90% of messages — sometimes intentional, sometimes a bug. Note the implied drop rate.
28. *Reliability mismatches between publisher and subscriber* break communication silently in some DDS implementations. Tabulate every topic where the publisher and subscriber QoS are not compatible.
29. For wireless or congested networks, flag any `RELIABLE` topic carrying high-rate sensor data — DDS reliability protocols backlog under loss and amplify the problem.
29a. For *late-joiner support*, confirm every topic carrying state-of-the-world content (current goal, current mode, last command echo) is TRANSIENT_LOCAL. A new operator UI that joins mid-mission should see the current state without waiting for the next update.
29b. For *bursty publishers*, check the queue depth on subscribers. A planner that publishes a new plan only on demand (sub-Hz) does not need a deep subscriber queue; a debug logger that buffers a recent window before crash-dumping might.
29c. Flag any *QoS profile customization that is undocumented*. A bespoke QoS profile with non-default reliability, durability, depth, and liveliness must have a one-line rationale in the code or it is technical debt waiting to bite.

### Stage 5 — Lifecycle and node states

30. Identify which nodes are *managed (lifecycle) nodes* and which are standard. Safety-critical and resource-heavy nodes — drivers, planners, controllers, sensor pipelines — benefit from being managed. A driver that is unmanaged either always runs or always crashes if its hardware is absent.
31. Check the *lifecycle transition strategy*. There should be a coordinator (a launch action, a manager node, or Nav2's lifecycle manager) that brings nodes through `configure → activate → deactivate → cleanup → shutdown` in a defined order. Missing coordination is a Major — relying on launch-time race conditions is a recipe for sim-only success.
32. Check that *resource allocation lives in `on_configure`* and *resource start lives in `on_activate`*. Subscribing to a topic in `on_configure` and starting the timer in `on_activate` is the pattern. Subscribing in the constructor defeats the purpose.
33. Check that *deactivation actually stops effect*. A lifecycle node whose `on_deactivate` does not stop the motor command publisher is not safely deactivatable. Audit each `on_deactivate` for completeness.
34. Check *error recovery*. A managed node that transitions to `ErrorProcessing` should have a documented recovery path — usually `configure` from `unconfigured` after a reset, with a bounded retry budget. Missing is a Minor in research, Major in production.
35. For *unmanaged nodes that probably should be managed*, recommend conversion. Common candidates: anything that owns hardware, anything that owns a large model in memory, anything that publishes safety-relevant data.

### Stage 6 — Message and interface design

36. For each custom message, check that *field units are encoded in the field name or documented in a comment*. `float64 angle` is a Major finding — radians or degrees, world or body frame, signed convention? `float64 angle_rad` resolves it.
37. Check *frame_id discipline*. Anything with spatial meaning (poses, twists, point clouds, transforms) must carry a `std_msgs/Header` with a populated `frame_id`. A `geometry_msgs/Pose` without a header is ambiguous — is it in `map`, `odom`, `base_link`?
38. Check *timestamp discipline*. Every sensor message and every state message carries a `stamp` populated from the source clock, not `now()`. Stamping at publish time defeats latency analysis.
39. Check *latency-critical messages for size*. A `PointCloud2` with `point_step` and `row_step` set but unused fields is wasted bandwidth. A custom message that nests `Image` plus metadata inside it forces full-copy even when only metadata is needed.
40. Check that *services are used for short request/response* and *actions are used for long-running operations with cancellation and feedback*. A planner exposed as a service is a Major design issue — the client has no way to cancel a 30-second plan.
41. Check that *parameters are used for configuration*, not as a back-channel for runtime data. A node that uses parameter callbacks to receive sensor readings is a smell — that is what topics are for.
42. Check *versioning* of custom interfaces. Once a message ships to a fleet, breaking changes are a redeployment event. New optional fields are safe; renaming or reordering is not. Flag custom messages that have no version strategy.

### Stage 7 — Parameters and configuration

43. Check that every node *declares* its parameters with `declare_parameter` and a type. Reading an undeclared parameter is a runtime error in newer distros.
44. Check for *parameter callbacks*. Nodes that change behavior on parameter updates should register a callback; nodes that need a restart to pick up new parameters should document that. The mix is a footgun.
45. Check that *secrets are not in parameter files*. Credentials, API keys, and certificates should be loaded from environment or a secret store, not from a YAML file checked in next to the launch.
46. Check that *parameter files are organized by deployment*, not by node. A single `params/robot_prod.yaml` with all node parameters is easier to audit than fifty per-node YAMLs scattered across packages.
47. Check that *defaults are sane*. A parameter that defaults to a value that is unsafe on hardware (e.g., max velocity defaulting to its physical limit rather than a safe fraction) is a Major.

### Stage 8 — Launch, namespaces, and isolation

48. Check that *launch files are composable*. A launch file that hard-codes paths or assumes a single robot is a Major in any multi-robot or any sim-then-real flow.
49. Check that *simulation and real launches share the maximum possible common configuration* — usually a base launch included by both, with sim-only and real-only overrides. Two divergent launch trees are a maintenance trap.
50. Check that *namespaces isolate robots*. Every node and every absolute topic that is robot-specific should live under a per-robot namespace. Global topics (e.g., a fleet manager) live at root.
51. Check that *remappings are consistent*. Remapping `cmd_vel` to `mobile_base/cmd_vel` in one launch and to `base/cmd_vel` in another is a smell.
52. Check that *launch handles failure*. If a node dies, what happens? `respawn=True` is appropriate for restartable services, dangerous for nodes that own state (a respawning driver may re-initialize hardware mid-motion). Document the choice.
53. Check *test isolation*. Integration tests should bring up only the nodes under test, with deterministic clocks (`use_sim_time`) and bounded timeouts. Tests that depend on the full system being up are not unit tests — they are end-to-end tests and should be labeled.

### Stage 9 — DDS, discovery, and middleware

54. Identify the *RMW implementation* (Cyclone DDS, Fast DDS, Connext, etc.). Different defaults — Cyclone defaults to unicast multicast disabled in some configurations; Fast DDS has different reliability heuristics. Flag where the choice is incidental rather than deliberate.
55. Check *ROS_DOMAIN_ID* and *ROS_LOCALHOST_ONLY* (or the equivalent middleware-specific settings). A robot left at the default domain on a shared lab network will see and be seen by every other ROS 2 system on that network. A Major in any shared environment.
56. Check *discovery scope*. Multicast discovery works on a LAN; across subnets or in cloud environments, recommend explicit discovery server configuration. Misconfigured discovery wastes engineer-days.
57. Check *security configuration* if SROS2 is in use. If it is not, document the trust assumption — anyone on the network can publish to any topic. For non-research deployments, recommend SROS2 or a network-layer alternative.
58. Check *bandwidth budget*. Sum the per-topic data rates against the network's realistic throughput, with a 50% headroom for retransmits and other traffic. Saturated Wi-Fi is the single most common field failure for mobile robots.

### Stage 10 — Time, clocks, and synchronization

59. Check that *every node respects `use_sim_time`*. A node that reads wall-clock time directly (e.g., `time.time()` in Python or `std::chrono::system_clock`) instead of the ROS clock will desync from simulation and from rosbag playback. A Major.
60. Check that *multi-machine systems use a synchronized clock*. NTP or PTP between machines; PTP for sub-millisecond requirements. Drift between machines breaks TF and breaks any latency analysis.
61. Check that *transforms are looked up with the correct time semantics*. `lookupTransform` with `Time(0)` (latest) is fast and tolerant; with a specific stamp is precise and brittle. Both have uses; flag mismatches.

### Stage 11 — Observability

62. Check that every node publishes *diagnostics* via `diagnostic_updater` or equivalent. A node that fails silently is invisible to the operator. Diagnostic frequency should be 1 Hz minimum; aggregated diagnostics surface to a single `/diagnostics_agg` topic that the operator UI consumes.
63. Check that *logging levels are calibrated*. `INFO` on every iteration of a 100 Hz loop floods the log and hides real events. Per-node log level configuration is the pattern; rate-limited logging macros (`RCLCPP_INFO_THROTTLE`, `RCLCPP_WARN_ONCE`) for repeating events.
64. Check that *rosbag recording is feasible* — the topic graph fits the bandwidth and disk budget of the recorder, and sensitive topics are excluded or anonymized. Bag rotation and retention are configured (24-hour rolling, on-crash full capture).
65. Check that *metrics export* exists — even a simple bridge that exposes node CPU, message rates, and queue depths to Prometheus or the team's stack lets the operator see degradation before it bites.
66. Check for *health endpoints* — a service or topic that summarizes "is this subsystem ready?" for the operator UI and for upstream coordinators. Lifecycle state alone is insufficient: a node may be ACTIVE but degraded.
67. Check for *operator UI signal coverage*. The set of topics, services, and state the operator can see should match the failure modes that can happen. A failure mode that has no UI signal is one the operator will not catch until it propagates.
68. Check that *latency between subsystems is observable*. End-to-end latency (sensor → fusion → planner → controller → actuator) is the canonical robot KPI; instrument the points where messages traverse and publish a derived latency topic.

### Stage 12 — Security and trust boundaries

69. Identify *trust boundaries*. Where does the system trust input from outside? Sensor data from physical inputs is trusted under physical-security assumptions; messages arriving from outside the robot (cloud, operator UI, fleet manager) cross a trust boundary and warrant authentication.
70. Identify *exposed surfaces*. Any topic, service, or action reachable from the network is reachable by an attacker on that network. The list of exposed surfaces should be small and deliberate.
71. Check *SROS2* status. If enabled, confirm certificate distribution, key rotation, and the trust chain. If disabled, document the threat model — anyone on the network can publish to any topic, including command topics.
72. Check *parameter-write authority*. Many ROS 2 distros allow any node on the same domain to write parameters on any other node. For safety-critical nodes (controllers, drivers), restrict or audit this.
73. Check *update authority*. A ROS 2 robot that pulls software updates from an arbitrary network source is a supply-chain risk. Updates should be signed and the trust root documented.
74. Check the *log redaction* policy. Logs commonly contain PII (when robots operate near humans), customer data, or sensitive operational data. Redaction at write time is the only reliable form.

### Stage 13 — Rank and render

75. Each finding has a severity: `Blocker` (safety, data loss, or guaranteed failure in production), `Major` (will bite under realistic conditions), `Minor` (smell, technical-debt), `Note` (informational, neutral choice).
76. The tier modifier: `production` and any tier interacting with humans biases each finding up one level if the failure mode is safety-relevant. `research-prototype` biases Minor down to Note for non-safety items.
77. Render the report with: an executive summary, a per-component scorecard (node graph, composition, executors, QoS, lifecycle, messages, parameters, launch, DDS, observability, security), a per-topic QoS table, a per-node lifecycle and executor table, and a prioritized rework list with effort estimates (S/M/L) where the agent can infer them.
78. The executive summary names the top three risks in plain language an engineering manager can act on without reading the rest of the report. If the agent cannot pick three, the system is in worse shape than a triaged report can capture and the executive summary says so.
79. The scorecard uses a five-state rubric per component: `Strong`, `Adequate`, `Needs Work`, `At Risk`, `Critical`. Anchored to evidence — a `Critical` rating cites the specific Blocker findings that produced it.
80. The rework list is prioritized by the product of severity and effort-discount: a Blocker that is a one-day fix outranks a Major that is a month-long rewrite. Surface both.
81. Render `findings_json` as a flat list, each entry `{id, severity, stage, node?, topic?, message_type?, finding, recommendation, tier, effort_estimate?}` for ingestion.
82. Where the agent is *uncertain* (e.g., the inventory does not include QoS declarations for some topics), surface the uncertainty in the report rather than silently assuming defaults. A review that quietly assumes everything missing is correct is a review that lies to its reader.

## Examples

A representative example: a four-wheeled mobile-ground robot with a lidar, a depth camera, an IMU, a planner, a controller, and a battery monitor — eight nodes across one SBC and one companion computer. The reviewer would likely flag:

- The lidar publishing `RELIABLE` across the SBC-companion boundary (should be `BEST_EFFORT` for sensor data; current setup will silently back-buffer under packet loss and OOM on the SBC).
- The planner exposed as a service rather than an action (no cancellation; a 30-second plan cannot be aborted by the BT when the goal becomes invalid).
- `/robot_description` published `VOLATILE` (late-joining RViz never sees the URDF; should be `RELIABLE`, `TRANSIENT_LOCAL`).
- The controller and planner sharing a single-threaded executor in the same composable container (controller callbacks are preempted during planning; recommend splitting into separate containers or a multi-threaded executor with reentrant callback groups).
- No namespace strategy — every topic at root (cannot run two of these robots side-by-side; pre-empts any future multi-robot capability).
- The battery monitor not being a lifecycle node (cannot be cleanly deactivated for testing; cannot be re-initialized after I2C glitches).
- `/tf` declared `RELIABLE` instead of `BEST_EFFORT, depth 100` (convention break that interacts badly with `tf2` clients expecting volatility).
- All nodes using `time.time()` in Python utility code paths (will desync from simulation and rosbag playback; `use_sim_time` is silently ignored).
- The launch file hard-coding `/dev/ttyUSB0` for the lidar (sim and real share the same launch; sim breaks because the device does not exist; recommend a launch argument with a sim-default of a mock driver).
- Default `ROS_DOMAIN_ID=0` on a shared lab network (the robot will see and be seen by every other ROS 2 system on the lab; recommend per-robot domain IDs and `ROS_LOCALHOST_ONLY=1` for sim).

A second example: a small manipulator-on-mobile-base with a perception pipeline (depth camera → object detection → grasp planner → arm motion planner → controller) and a Nav2 stack for the base. Twenty-three nodes across two machines. The reviewer would tabulate the QoS for every topic, identify that the object-detection node publishes raw 1080p images downstream when only the inference result is needed (gross bandwidth waste), flag the grasp planner and arm motion planner racing on a shared parameter `current_grasp_pose` (parameter abuse as IPC — should be a topic), and note that the lifecycle manager brings up the perception pipeline before localization is confirmed (the first detection happens against a transform tree that has not yet stabilized, and the first grasp pose is therefore wrong).

## Worked walkthrough

To make the methodology concrete, here is a walkthrough of the reviewer applied to a hypothetical input. The input is a `ros2 node list` plus `ros2 topic list -t` dump from a five-node mobile robot:

```
/laser_driver           publishes /scan (sensor_msgs/LaserScan)
/imu_driver             publishes /imu/data (sensor_msgs/Imu)
/localization           subscribes /scan, /imu/data, publishes /amcl_pose, /tf
/planner_controller     subscribes /amcl_pose, /goal_pose, publishes /cmd_vel
/battery_monitor        publishes /battery_state, /diagnostics
```

The reviewer would proceed:

**Stage 1 inventory.** Five nodes, four topics inbound to `planner_controller`, no namespace strategy, no transform from `base_link` to `laser_link` evident (presumably static via robot_state_publisher, which is absent from the list — Major: `robot_state_publisher` missing or undeclared). Custom messages: none. Implicit dependency on `/tf` and `/tf_static` — neither in the list (Major: TF tree not characterized).

**Stage 2 composition.** Five nodes, five processes, no composition. `/scan` flows from driver process to localization process — inter-process copy of LaserScan at 10-40 Hz. Flag as a Major performance optimization opportunity: compose `laser_driver` + `localization` into a container with intra-process comms.

**Stage 3 executors.** No executor information provided — request the team specify. If default single-threaded, `planner_controller` is suspect: planning and control in one node on one executor is a deadlock risk and a preemption risk. Recommend splitting into two nodes (planner + controller) and a multi-threaded executor with reentrant callback groups.

**Stage 4 QoS.** Tabulate:

| Topic | Type | Recommended QoS | Likely default | Finding |
| --- | --- | --- | --- | --- |
| /scan | LaserScan | BEST_EFFORT, VOLATILE, depth 5 | RELIABLE, depth 10 | Major: backlog risk |
| /imu/data | Imu | BEST_EFFORT, VOLATILE, depth 5 | RELIABLE | Major: same |
| /amcl_pose | PoseWithCovarianceStamped | RELIABLE, VOLATILE, depth 10 | RELIABLE, depth 10 | OK |
| /goal_pose | PoseStamped | RELIABLE, TRANSIENT_LOCAL, depth 1 | RELIABLE, VOLATILE, depth 10 | Major: late-joining UI never sees current goal |
| /cmd_vel | Twist | RELIABLE, VOLATILE, depth 1 | RELIABLE, depth 10 | Minor: depth could be 1 |
| /tf | TFMessage | BEST_EFFORT, VOLATILE, depth 100 (convention) | check tf2 default | confirm |
| /battery_state | BatteryState | RELIABLE, VOLATILE, depth 1 | RELIABLE, depth 10 | OK |
| /diagnostics | DiagnosticArray | RELIABLE, VOLATILE, depth 10 | RELIABLE | OK |

**Stage 5 lifecycle.** None of the nodes are lifecycle. The laser driver and the planner_controller should be — both own resources, both are safety-relevant. Major finding: convert to lifecycle and add a lifecycle manager.

**Stage 6 messages.** No custom messages. All standard. No findings.

**Stage 7 parameters.** Not in the input — request the team include parameter files.

**Stage 8 launch.** Not in the input — request the launch file.

**Stage 9 DDS.** Not in the input — request `ROS_DOMAIN_ID` configuration and RMW choice.

**Stage 10 time.** Not in the input — request `use_sim_time` configuration and confirm node code uses `node.get_clock()`.

**Stage 11 observability.** `/diagnostics` is published but `/diagnostics_agg` is not visible — recommend a diagnostic aggregator. No metrics export — recommend at minimum a CPU and message-rate exporter.

**Stage 12 security.** `ROS_DOMAIN_ID` not specified — Major in any shared network.

**Stage 13 render.** Executive summary: "Five-node stack with several Major findings clustered around QoS, lifecycle, and inter-process composition. The system will likely work in a quiet lab and fail under load. Recommended sequence of fixes: introduce robot_state_publisher and characterize the TF tree, set QoS profiles deliberately, convert hardware-owning nodes to lifecycle, compose laser+localization, and split planner from controller." Scorecard: node graph = Adequate, composition = Needs Work, executors = At Risk (pending data), QoS = At Risk, lifecycle = Needs Work, messages = Strong, parameters = unknown, launch = unknown, DDS = unknown, observability = Needs Work, security = At Risk.

This walkthrough is illustrative. Real systems are larger and have richer data; the methodology scales the same way.

## Reference patterns the reviewer recognizes as healthy

These are the shapes the reviewer compares the input against. None is mandatory — they are the calibration points.

- **Sensor publisher**: lifecycle node, BEST_EFFORT sensor_data QoS, header-stamped at acquisition time, frame_id matches the URDF link, diagnostics published at 1 Hz with the actual sensor rate observed, intra-process composition with downstream consumers on the same machine.
- **Latched state publisher** (map, URDF, calibration): RELIABLE + TRANSIENT_LOCAL, depth 1, published once at activation, never republished unless content changes, comes from a lifecycle node so subscribers know when it is stale.
- **Command topic**: RELIABLE, VOLATILE, small depth, single authoritative publisher (deadlocks and confusion arise from multiple `/cmd_vel` publishers), subscriber on the actuator side validates ranges and rejects malformed commands rather than crashing.
- **Action server for long work**: native ROS 2 action (not a service or topic pair), proper goal-handle accept/reject, feedback at a sensible rate (1-5 Hz, not every iteration), respects cancellation deterministically and within a documented bounded time.
- **Lifecycle coordinator**: a single launch action or manager node that owns the activation order, with explicit dependencies (perception before planning, planning before control) and a documented startup time budget.
- **Composable container**: 2-5 nodes that pass large messages between themselves, in the same process, intra-process comms enabled, multi-threaded executor sized to reserved CPU cores, fault domain documented (this container goes down together).
- **Parameter file**: per-environment YAML organized by node name, no secrets, defaults are *safe* values (low speeds, high tolerances), every parameter is declared in code with a type, parameter callbacks are documented or absent.

## Anti-patterns the reviewer flags immediately

- **`time.time()` in node code** (Python) or `system_clock::now()` (C++) instead of the node's clock — breaks sim time, breaks rosbag replay.
- **Synchronous service call inside a callback on a single-threaded executor** — guaranteed deadlock the first time the service implementation lives on the same executor.
- **A `/cmd_vel` topic with two publishers and no muxer** — the controller and the teleop both publish; the actuator alternates randomly and the robot lurches.
- **`/tf` with `RELIABLE` reliability** — `tf2` consumers expect default volatile semantics; reliability stalls under loss and breaks the transform tree.
- **Custom message with `float64 angle`** — no units, no frame, no convention. Becomes a multi-engineer-day bug in the field.
- **Parameter abuse as IPC** — using `set_parameters` from one node on another node as a runtime data channel. Topics exist for this.
- **`respawn=True` on a node owning hardware** — when the driver crashes mid-motion and respawns, it re-initializes the actuator and any state-machine assumptions are violated.
- **A single launch file with a 50-deep tree of includes** — unreviewable; encourages copy-paste; usually hides hard-coded dev-machine paths.
- **Mixed wall-clock and ROS-clock waits in the same node** — `time.sleep()` next to `node.get_clock().sleep_until()`. The two behave differently under sim time.
- **Production deployment at `ROS_DOMAIN_ID=0`** — collision risk on any shared network; every other ROS 2 system is visible.

## Outputs

The skill emits two artifacts. The first is a markdown `architecture_review` with the structure described in Stage 13 — narrative findings, component scorecard, per-topic and per-node tables, and a prioritized rework list. The second is `findings_json`, a flat array suitable for ingestion into a review bot, a CI gate, or a planning tool to track remediation.

The report opens with the executive summary; the rework list closes it. Engineers asked to "just give me the punchlist" can jump straight to the rework list and trust that severity and ordering reflect the full review.

## Integration into the team's process

The review is most useful when it lands in a place the team will act on. The agent recommends one of these landing spots, picked by team shape:

- *PR-comment bot*: the `findings_json` becomes inline comments on a PR that changes node graph, QoS, or message definitions. Best for active development phases.
- *Architecture decision record*: the markdown report becomes the body of an ADR captured in the team's docs. Best for milestone audits — pre-launch, pre-acquisition, pre-major-refactor.
- *Backlog import*: each Blocker and Major becomes a backlog ticket with its severity, rationale, and effort estimate already filled in. Best for teams with engineering managers who triage from a backlog.
- *Operator briefing*: the executive summary plus the rework list becomes a one-page brief for the field operations team. Best when the field team needs to know what shortcomings to watch for.

The agent does not enforce a landing spot; it produces both artifacts and lets the team choose. Where the team has a known process (e.g., the team uses Linear and tickets follow a template), the agent can adapt the `findings_json` to that template format on request.

## Repeat-review cadence

A one-time architecture review captures a point in time. The systems change, and unreviewed change accumulates back into the same shape that prompted the original review. The agent recommends:

- *Continuous*: PR-level review on changes that touch the node graph, custom messages, QoS choices, lifecycle, executors, or launch — automated via a CI hook that re-runs this skill on diffs.
- *Quarterly*: full re-audit on the current `main` snapshot, with the prior report attached so the agent can call out regressions and progress.
- *Pre-deployment*: before any deployment to a customer fleet, or before a step change in robot capability (new sensor, new hardware revision, new operating environment), a focused re-audit of the affected scope.
- *Post-incident*: if a field incident is suspected to have an architecture root cause (e.g., a deadlock, a QoS misuse, a recovery loop), an incident-focused audit narrowed to the implicated subsystem.

The agent caches the prior report's hash (when provided) and uses it to identify regressions in the next pass.

## Limitations

The reviewer reads what the team provides. It cannot:
- Measure real latencies, packet loss, or jitter — that requires runtime traces and rosbags.
- Verify that the launch graph actually matches the running system — a `ros2 node list` snapshot is a sanity check the agent will request.
- Replace simulation, hardware-in-the-loop testing, or safety review by qualified robotics engineers.
- Detect algorithm-level bugs inside a node (the agent reviews the graph and interfaces, not internal logic).
- Validate driver behavior against hardware — the reviewer assumes the team has separately confirmed the driver works as documented.
- Substitute for an in-person walkthrough with the engineers who built the system. A skilled human review catches context that a graph-and-config audit cannot.

Findings are advisory. Before any change touches a robot capable of motion, the change must be validated in simulation, on a bench rig with motion physically constrained, and only then in the field with a kill switch and a human supervisor. The team owning the robot owns the deployment decision; the agent's role is to surface what can be surfaced from the architecture artifacts and to make the implicit trade-offs visible.

## Sources reviewed

- https://github.com/ros2/ros2
- https://github.com/ros2/rclcpp
- https://github.com/ros2/rmw
- https://github.com/ros2/design
- https://github.com/ros2/launch
- https://github.com/ros2/common_interfaces
- https://github.com/ros2/demos
- https://github.com/ros-controls/ros2_control
- https://github.com/ros-navigation/navigation2
- https://github.com/micro-ROS/micro_ros_setup
