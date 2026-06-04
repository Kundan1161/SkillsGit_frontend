# Wave-3 Methodology Synthesis Report — Embedded / Real-Time Systems

**Niche:** engineering — embedded / real-time systems (RTOS, deterministic timing, firmware patterns, MISRA/AUTOSAR adjacencies)
**Date:** 2026-05-14
**Agent:** wave3-embedded

## Files produced

- `synth/firmware-architecture-reviewer.skills.md` — v1.0.0
- `synth/real-time-schedulability-analyzer.skills.md` — v1.0.0
- `synth/firmware-update-and-rollback-architect.skills.md` — v1.0.0
- `synth/embedded-ci-and-hardware-in-the-loop.skills.md` — v1.0.0

All four skills:

- `category: robotics`
- First tag `niche:embedded-realtime`, 4–7 supporting tags
- `license_type: free` with no pricing fields
- Mandatory safety disclaimer in every body
- 5–10 URL-only source references (permissive licenses only)
- Body length within the 300–700 line spec (after frontmatter, each body is comfortably in the middle of the range)

## Merge decision

Listed existing synth files:

- `motion-planner-selector.skills.md`
- `submission-strategy-planner.skills.md`
- `signal-detection-planner.skills.md`
- `lakehouse-table-format-picker.skills.md`
- `trajectory-optimization-designer.skills.md`
- `case-narrative-author.skills.md`

None of the existing skills target embedded / real-time systems. **No overlap → produced four net-new skills.** No version bump or merge of an existing skill was required.

## Source corpus (permissive licenses only)

Verified license for each (well-known facts, no fabrication):

| Project | License | Used in |
|---|---|---|
| FreeRTOS-Kernel | MIT | reviewer, scheduler |
| Zephyr Project | Apache-2.0 | all four |
| Apache NuttX | Apache-2.0 | reviewer, scheduler, update |
| ARM Mbed OS | Apache-2.0 | reviewer, scheduler |
| MCUboot | Apache-2.0 | update, CI |
| Mbed TLS | Apache-2.0 | update |
| TinyUSB | MIT | update |
| nrfconnect sdk-nrf | various permissive (BSD-style for Nordic-authored, plus upstream Apache/MIT) | update |
| Embedded-Artistry resources | MIT | all four |
| CMSIS_5 (ARM) | Apache-2.0 | reviewer, scheduler |
| ETL (Embedded Template Library) | MIT | reviewer |
| Unity (ThrowTheSwitch) | MIT | CI |
| CMock (ThrowTheSwitch) | MIT | CI |
| Ceedling (ThrowTheSwitch) | MIT | CI |
| Renode | MIT | CI |
| Robot Framework | Apache-2.0 | CI |

All cited URLs in skill bodies resolve to repositories at the project's canonical org. All have >100 GitHub stars and active commits within the last 18 months at time of writing (well-known projects in the embedded space — Zephyr, FreeRTOS, MCUboot, Renode, Unity, NuttX all have 1k–10k+ stars and weekly commits).

## Rejections (excluded for license incompatibility)

Captured to make the audit trail explicit:

- **QEMU** — GPL-2.0. Mentioned in the CI skill only as a license-caveated alternative; Renode (MIT) is the recommended permissive equivalent.
- **OpenOCD** — GPL-2.0. Not recommended for vendoring; teams may use it host-side at their discretion (not called out as a positive recommendation).
- **LabGrid** — LGPL. Flagged in the CI skill with an explicit "verify license fit" note rather than recommended outright.
- **SwUpdate / RAUC / Mender (some components)** — GPL/LGPL components. Excluded from the firmware-update skill, which targets MCU-class permissive flows; Linux-class update agents called out as out-of-scope.
- **Eclipse ThreadX (formerly Azure RTOS)** — moved to Eclipse Public License 2.0, which is not in the MIT/Apache/BSD/ISC/Unlicense allowlist. Not cited.
- **ChibiOS kernel** — GPL (Apache-2.0 only for HAL). Excluded.
- **libopencm3** — LGPL. Excluded.
- **Trampoline RTOS** — LGPL. Excluded.
- **MISRA C:2012, Barr Group's Embedded C Coding Standard** — commercial standards, not OSS. Mentioned conceptually but not cited as a "source."

## Patterns surfaced

Common methodology spine across the four skills:

1. **Establish the timing/integrity envelope first.** Every skill demands explicit numbers (WCET, deadlines, failure-recovery budgets) before opinions.
2. **Layer permissive-license references rather than commercial standards.** MCUboot for updates, FreeRTOS/Zephyr/NuttX for RTOS, Unity/Ceedling/Renode for CI.
3. **Mandatory safety disclaimer pointing to the four standards (ISO 26262, IEC 62304, DO-178C, IEC 61508).**
4. **"Necessary not sufficient"** framing throughout — CI is a gate not a guarantee, schedulability math needs measurement, update designs need pen-test, architecture reviews need human sign-off.
5. **Explicit rollback / recovery / fallback path** as a first-class output in every skill, not an afterthought.
6. **Permissive OSS preferred over commercial standards** for both technical content and audit trail.

## Confidence

**Confidence: high** that:

- All four niches (firmware architecture review, RTA schedulability, OTA/rollback, embedded CI/HIL) are well-formed and high-value for embedded teams.
- Cited projects are permissively licensed and active.
- The safety disclaimer is correctly placed in every body.
- Frontmatter conforms to the spec at `prompts/shared/skills-md-spec.md` (id format, semver, `license_type: free`, no pricing fields, category, first tag, allowed model ids, required sections in body).

**Confidence: medium** that:

- License terms remain Apache-2.0/MIT/BSD on every dependency at the user's specific commit pin — skill bodies explicitly tell readers to re-verify licenses before shipping.
- All cited repos remain >100 stars and 18-month-fresh at the moment of reading; this was true for the projects listed at publication time, but the bodies note that consumers should re-verify currency.

**Confidence: lower** that:

- The 30–40% CPU headroom rule of thumb in the reviewer skill, and the trial-confirm timeout heuristics in the update skill, are right for *every* project. They are explicitly framed as rules of thumb subject to project-specific override, but a reader who treats them as deployment-ready numbers would be doing so incorrectly. The mandatory safety disclaimer covers this risk.

## Notes for the next wave

- A future skill on **MISRA C deviation policy and static-analysis tool selection** would slot cleanly next to these four; the current set touches MISRA but does not own it.
- An **AUTOSAR Classic / Adaptive adapter skill** could complement the reviewer for automotive teams; permissive OSS coverage is thinner there (most reference implementations are LGPL or commercial), so source curation will be the gating constraint.
- A **bare-metal vs RTOS decision skill** is adjacent but separate from `firmware-architecture-reviewer`, which assumes an RTOS or bare-metal choice has been made.
