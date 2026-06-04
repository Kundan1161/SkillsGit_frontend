# Wave-4 Methodology Recovery — Visual-Inertial SLAM

**Niche:** robotics / visual-inertial SLAM and VIO methodology
**Date:** 2026-05-14
**Author handle:** skillsgit-curated

## Files produced

Four skill files in `apps/api/scripts/seed_data/synth/`:

1. `vio-slam-system-architect.skills.md` — end-to-end VI-SLAM architecture methodology (sensor selection, calibration regime, front-end/back-end split, tight vs loose coupling, loop closure, drift mitigation, multi-session map persistence, observability, validation).
2. `slam-failure-mode-investigator.skills.md` — diagnostic methodology for failing VI-SLAM stacks (failure bracketing, telemetry snapshot, hypothesis enumeration across calibration / texture / parallax / dynamics / lighting / motion / sync / bias-observability / loop-closure / numerical / regime, layered mitigations, experiment design, validation).
3. `slam-evaluation-rig-designer.skills.md` — methodology for designing a SLAM evaluation rig (performance rubric, metric set, ground-truth strategy, environment-and-motion coverage matrix, regression suite, hardware-in-loop harness, release gates, dashboards, ownership, rig evolution).
4. `lidar-inertial-fusion-architect.skills.md` — methodology for LiDAR-inertial odometry and mapping architectures (sweep-vs-motion framing, IMU front-end, point-cloud preprocessing, scan registration, factor-graph back-end, degeneracy handling, real-time engineering, map persistence).

Each file passes the spec's required sections (`## When to use`, `## How to apply`) and includes the mandatory safety disclaimer verbatim. Tag set leads with `niche:visual-inertial-slam` plus 6-7 supporting tags per skill.

## Source URLs reviewed (with licenses)

Reviewed via WebFetch on the project READMEs; license stated as found on each project page.

- https://github.com/UZ-SLAMLab/ORB_SLAM3 — GPL-3
- https://github.com/MIT-SPARK/Kimera-VIO — BSD-2
- https://github.com/rpng/open_vins — GPL-3
- https://github.com/HKUST-Aerial-Robotics/VINS-Mono — GPL-3
- https://github.com/HKUST-Aerial-Robotics/VINS-Fusion — GPL-3
- https://github.com/stella-cv/stella_vslam — BSD-2 (with mixed third-party licenses noted in repo)
- https://github.com/SpectacularAI/HybVIO — Apache-2.0
- https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam — Apache-2.0
- https://github.com/MIT-SPARK/Ouroboros — BSD-2
- https://github.com/hku-mars/FAST_LIO — GPL-2
- https://github.com/TixiaoShan/LIO-SAM — BSD-3
- https://github.com/gaoxiang12/faster-lio — GPL-2
- https://github.com/hku-mars/FAST-LIVO — GPL-2
- https://github.com/hku-mars/FAST-LIVO2 — GPL-2
- https://github.com/MichaelGrupp/evo — GPL-3
- https://github.com/Hilti-Research/hilti-trimble-slam-challenge-2026 — research dataset

Per the wave-4 policy change, previously-rejected GPL/AGPL/CC-BY-SA repos were read for methodology study and cited transparently with license tags. None of these projects' source text, code, or close paraphrase appears in the skill bodies.

## Patterns identified across sources

Common architectural patterns observed across the surveyed projects (described generically, not anchored to any specific repo):

- **Tightly-coupled fusion is the modern default.** Visual residuals and IMU residuals are jointly optimized against a shared state across all the surveyed VI-SLAM systems regardless of back-end style.
- **IMU pre-integration is the universal bridge.** Inertial samples between keyframes are compacted into a single relative-motion constraint with a bias-aware Jacobian. The specific algebra varies; the role does not.
- **Two front-end families dominate.** Indirect (feature/descriptor) and direct (photometric). Hybrid approaches exist.
- **Three back-end families dominate.** Sliding-window filtering (MSCKF-style), sliding-window nonlinear optimization, and full-graph incremental smoothing. The choice maps to compute envelope and failure-cost tolerance.
- **Loop closure is layered.** Appearance candidate → geometric verification → consistency screen → robust factor injection. Single-stage place recognition is universally avoided.
- **Health monitoring is treated as part of the system.** Track count, residual chi-squared, pre-integration uncertainty, bias-observability proxies. Surfaces the graceful-degradation policy in production stacks.
- **Multi-session is an explicit subsystem.** Map server, append-only merging, gated promotion, immutable golden baseline.
- **LiDAR-inertial systems share most of this structure** but add point-cloud preprocessing, motion undistortion driven by IMU prediction, and explicit degeneracy detection for corridors and open spaces.
- **Evaluation methodology converges on ATE/RPE plus environment-coverage matrices.** Tooling like `evo` provides a baseline; the surrounding rig (datasets, harness, gates, dashboards) is what differentiates a research evaluation from a product one.

## Boundary checks against existing skills

The existing `slam-stack-architect.skills.md` is broad and library-recommending across LiDAR + visual + VIO. To avoid duplication, the new skills:

- `vio-slam-system-architect` deliberately stays library-agnostic in the body, goes deeper on coupling / pre-integration / bias observability / multi-session, and tagged with `niche:visual-inertial-slam` rather than `niche:motion-planning`.
- `slam-failure-mode-investigator` covers a different verb (diagnose, not architect) with no overlap.
- `slam-evaluation-rig-designer` covers a different verb (evaluate) with no overlap.
- `lidar-inertial-fusion-architect` overlaps in topic with the existing `slam-stack-architect` but is deeper on the LiDAR-specific methodology (sweep-vs-motion framing, motion undistortion, degeneracy detection, real-time engineering). I placed it in the visual-inertial niche per the policy framing, but it is genuinely a LiDAR-inertial methodology document.

Existing `robot-perception-stack-architect` is broader (full perception stack including fusion architectures and ODD coverage); no body-level duplication. `robot-camera-lidar-calibration-planner` is dedicated to calibration; the new VIO architect skill references calibration at the methodology level but defers operational procedure to that dedicated skill.

## Methodology-vs-expression boundary checks

Steps taken to confirm no source paraphrase appears:

1. **Cited material was summarized, not transcribed.** WebFetch was used with explicit prompts asking for structural summaries and brief listings, not verbatim text. The fetched summaries were then re-organized and re-expressed into the skills' own framework.
2. **No trademarked product names appear in body content.** The strings "ORB-SLAM", "FAST_LIO", "Kimera", "OpenVSLAM", "LIO-SAM", "VINS-Mono", "VINS-Fusion", "OpenVINS", and any other product-name tokens appear only in `## Sources reviewed` URL citations. Each skill body refers to underlying techniques generically ("sliding-window filtering", "indirect sparse front-end", "place-recognition descriptor index", "scan-to-map registration", etc.).
3. **No section headings copied.** Each skill's section headings are original ("Frame the platform's motion and compute envelope", "Bracket the failure", "Construct the environment-and-motion matrix", "Frame the platform motion and the LiDAR cadence"). They do not mirror the section names found in surveyed READMEs.
4. **Tables and code blocks deliberately omitted.** Surveyed repos use specific tables and code samples; the skills bodies use prose lists and avoid the comparison-table format. (One internal table-shaped construct in the existing `slam-stack-architect` was noted; the new VIO skill avoids it.)
5. **Spot-checks for distinctive phrasings.** Phrases that recur across the surveyed projects (e.g. "a robust and versatile" or "tightly-coupled iterated extended Kalman filter") were deliberately avoided. The skills describe these ideas in independent phrasing ("filtering with sliding-window marginalization", "iterative state correction with bias-aware Jacobians").
6. **No code, no formulae copied.** All methodology is described in prose; no equations or pseudocode were taken from any source.
7. **Generic example data only.** The worked examples use generic deployments (warehouse robot, inspection drone, handheld scanner) rather than mirroring any source's example.

## Confidence

- **Methodology coverage:** High. The four skills together cover architect / diagnose / evaluate, which is the durable verb triplet for this niche. LiDAR-inertial is included as an adjacent methodology because of substantial overlap with the visual-inertial side, with explicit framing of the relationship.
- **Originality:** High confidence that no paraphrase close to source phrasing appears. Bodies were drafted from the synthesized mental model after reviewing the structural summaries, not from the summaries verbatim.
- **License transparency:** High. Every source is cited with a license tag; the buyer can audit. Several cited sources are GPL/Apache/BSD; per wave-4 policy these are acceptable as methodology-study citations because no source content is reproduced.
- **Trademark posture:** Trademarked names appear only in URLs in `## Sources reviewed`. Frontmatter, body content, examples, and trigger keywords contain no trademarked names.
- **Spec validity:** Frontmatter conforms to `prompts/shared/skills-md-spec.md`. Required sections (`## When to use`, `## How to apply`) present. Body length per skill is within the 300-600 line target. Mandatory safety disclaimer present verbatim in every body.
- **Open risk:** The wave-4 policy change is novel; if downstream legal review re-tightens to "permissive licenses only" for citations, the GPL/AGPL citations would need to be removed. The methodology bodies would still stand because no source content is incorporated; only the source list would be trimmed.
