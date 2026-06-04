# Wave-3 Synthesis Report — Robotics: Motion Planning & Kinematics

## Scope

Niche: **robotics — motion planning & kinematics** (path planning, trajectory optimization, collision avoidance, SLAM).

## Pre-existing synth state

The `D:\skillsgit\synth\` directory did not exist prior to this run. No merges were required. All four skills below are net-new.

## Deliverables

Four skills, all `license_type: free`, all under the marketplace skills.md spec, all carrying the mandatory motion-planning safety disclaimer in the body:

1. `synth/motion-planner-selector.skills.md` — recommends a planner family (sampling, optimization, search, hybrid) and collision-checking strategy given robot DoF, environment, and task. Decision matrix included.
2. `synth/trajectory-optimization-designer.skills.md` — frames trajectory-optimization problems: formulation (collocation vs shooting vs DDP), cost, constraints, initialization, smoothing, real-time vs offline, validation.
3. `synth/slam-stack-architect.skills.md` — designs SLAM stacks from sensor suite + platform + environment: front-end, back-end, loop closure, map representation, drift mitigation, persistence, multi-session, validation.
4. `synth/collision-checking-strategy.skills.md` — picks broad-phase + narrow-phase, discrete vs CCD, safety margins, acceleration structures, lazy vs eager, and the GPU decision.

Each skill body is 300–500 lines, conforms to the required sections (When to use, How to apply, Inputs, Outputs, Examples, Limitations), and ends with 6–7 URL-only source references.

## Tagging

- `category: robotics` on all four skills.
- First tag on all four: `niche:motion-planning`.
- Additional tags 4–7 per skill, covering the specific subtopic (RRT, PRM, CHOMP, LiDAR, VIO, FCL, BVH, etc.).

## License verification (all verified via WebFetch on canonical sources)

Permissive (used as references in the skills):

- **OMPL** — BSD-3-Clause (Rice University). Verified at the OMPL license page and ompl/ompl LICENSE.
- **MoveIt 2** — BSD-3-Clause. Verified at moveit/moveit2.
- **Cartographer** — Apache-2.0. Verified at cartographer-project/cartographer.
- **RTAB-Map** — BSD (3-Clause). Verified at introlab/rtabmap LICENSE.
- **Open3D** — MIT. Verified at isl-org/Open3D LICENSE.
- **Crocoddyl** — BSD-3-Clause. Verified at loco-3d/crocoddyl LICENSE.
- **FCL** — BSD. Verified at flexible-collision-library/fcl LICENSE.
- **Drake** — BSD-3-Clause. Verified at RobotLocomotion/drake LICENSE.TXT.
- **Pinocchio** — BSD-2-Clause. Verified at stack-of-tasks/pinocchio.
- **AIKIDO** — BSD-3-Clause. Verified at personalrobotics/aikido.
- **Kimera-VIO** — BSD-2-Clause. Verified at MIT-SPARK/Kimera-VIO.
- **Nav2** — Apache-2.0 default, but mixed-license repo (some packages LGPL-2.1-or-later). Cited cautiously in `motion-planner-selector` with explicit "check per-package" note.

Rejected:

- **ORB-SLAM3** — **GPLv3**. The most-cited visual-inertial SLAM in academia, but copyleft incompatible with marketplace and most proprietary use. Explicitly named in `slam-stack-architect` as "not recommended" so readers know why it is absent.
- **TRAC-IK** (HIRO Panda fork at minimum) — **LGPL-2.1**. Out of the allowed license set (MIT/Apache/BSD/ISC/Unlicense). Dropped; not referenced in any skill. The original TRACLabs Bitbucket source could not be confirmed in this session.

## Patterns used across the four skills

- **Mandatory safety disclaimer** — full required text in every body.
- **"Refuse to declare done"** — every skill ends its methodology with an explicit validation checklist (sim regression, caged hardware soak, failure-mode handlers).
- **License-note discipline** — each library citation includes the verified license in parentheses; readers are reminded to re-verify before vendoring.
- **Tradeoff-first framing** — no skill recommends a single tool; each gives a primary + fallback or a decision matrix.
- **Bench → sim → caged-hardware progression** — appears verbatim in all four validation plans to discourage shortcut deployments.

## Source citations (used in skill bodies)

- https://github.com/ompl/ompl
- https://github.com/moveit/moveit2
- https://github.com/RobotLocomotion/drake
- https://github.com/personalrobotics/aikido
- https://github.com/flexible-collision-library/fcl
- https://github.com/ros-navigation/navigation2
- https://github.com/isl-org/Open3D
- https://github.com/loco-3d/crocoddyl
- https://github.com/stack-of-tasks/pinocchio
- https://github.com/cartographer-project/cartographer
- https://github.com/introlab/rtabmap
- https://github.com/MIT-SPARK/Kimera-VIO

Per skill, 6–7 are cited (within the 5–10 bound). No duplicate sets across skills; each skill cites the libraries most relevant to its decisions.

## Confidence

**High** on license verification for the recommended permissive libraries — each was checked at the canonical LICENSE file or upstream license page.

**High** on methodology accuracy — content reflects mainstream practice taught in modern motion-planning literature and the documented APIs of OMPL / MoveIt / Drake / Cartographer / RTAB-Map. No novel claims; the skills are synthesizing methodology, not proposing new algorithms.

**Medium-high** on the Nav2 license note — Nav2 is a mixed-license meta-repo; per-package verification is required at vendoring time, and the skill body says so.

**Medium** on the completeness of advanced topics — learned planners (diffusion policies, RL), NeRF/Gaussian-splatting SLAM, soft-robot collision, and contact-implicit trajectory optimization are flagged as out-of-scope rather than covered. This is appropriate for a methodology-synthesis skill aimed at production decisions.
