# Curation report — Robotics: functional safety, hazard analysis, ISO 13849 / IEC 61508 / ISO 10218 / ANSI R15.06

## Source-thinness disclosure (read this first)

This niche is **genuinely sparse** on permissive-licensed GitHub content. Functional-safety methodology is overwhelmingly carried by:
- Paywalled standards bodies (ISO, IEC, SAE, RIA) — not redistributable, not in scope.
- Academic publications (MIT STAMP/STPA group, York GSN group) — typically CC-BY or CC-BY-NC, not in the MIT/Apache/BSD/ISC/Unlicense allowlist.
- Vendor whitepapers (manufacturer-locked, no license).
- Consulting-firm templates (proprietary or CC-BY-NC-SA).

Public GitHub repositories that (a) cover hazard analysis, safety cases, FMEA, STPA, ISO 13849, IEC 61508, or robot safety review and (b) carry MIT / Apache / BSD / ISC / Unlicense are scarce. Many candidates rejected (see Rejections). The synthesis therefore leans on a small set of strictly-permissive sources from the adjacent operational-safety and verification-tooling space, and the methodology is original to this skill set rather than borrowed from any single source. Three skills produced (not five-to-ten) reflecting the source-thinness disclosure in the brief.

## Files produced

1. `D:\skillsgit\apps\api\scripts\seed_data\synth\robot-hazard-analysis-conductor.skills.md`
2. `D:\skillsgit\apps\api\scripts\seed_data\synth\safety-requirements-deriver.skills.md`
3. `D:\skillsgit\apps\api\scripts\seed_data\synth\pre-deployment-safety-review.skills.md`

## Skills overview

| Skill | License model | Price | Length-driving sections |
|---|---|---|---|
| Robot Hazard Analysis Conductor | free | — | 12-move analysis, four-question UCA structure, standard layout (losses → hazards → CAs → UCAs → scenarios → constraints → mitigations → residuals → open questions) |
| Safety Requirements Deriver | free | — | 11-move derivation, four-category structure (functional / performance / monitoring / fail-safe), allocation matrix, integrity-target placeholders |
| Pre-Deployment Safety Review Designer | free | — | 12-move plan, 6-stage gated review, kill-switch protocol, observer roles, abort/rollback path, post-deployment window |

All three skills carry the **mandatory extra-strong disclaimer** at head and foot, and repeat the no-PL/SIL/category-assignment caveat explicitly. All three name "qualified safety engineer" and "notified-body assessment" as the authoritative path.

## Sources per skill (all verified MIT or Apache-2.0)

### Robot Hazard Analysis Conductor (6 sources)
- https://github.com/voyage/open-autonomous-safety — MIT, 180 stars (relaxed-threshold-disclosed; safety-process documentation for AV operations)
- https://github.com/github/codeql-coding-standards — MIT, 202 stars (ISO 26262 qualified tool; safety-standards verification framing)
- https://github.com/davidski/evaluator — MIT, 184 stars (quantitative risk methodology; FAIR ontology — adjacent, used for risk-framing discipline)
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0, ~1k stars (severity, response discipline)
- https://github.com/counteractive/incident-response-plan-template — Apache 2.0, 779 stars (response plan structure)
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0, 1.1k stars (playbook structure; sample code MIT-0, documentation portions are CC-BY-SA and were NOT consulted for prose patterns — only the structural conventions of the sample-code playbooks)

### Safety Requirements Deriver (5 sources)
- https://github.com/voyage/open-autonomous-safety — MIT, 180 stars
- https://github.com/github/codeql-coding-standards — MIT, 202 stars (ISO 26262 tool qualification framing)
- https://github.com/davidski/evaluator — MIT, 184 stars
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0
- https://github.com/counteractive/incident-response-plan-template — Apache 2.0

### Pre-Deployment Safety Review Designer (6 sources)
- https://github.com/voyage/open-autonomous-safety — MIT, 180 stars
- https://github.com/github/codeql-coding-standards — MIT, 202 stars
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0
- https://github.com/counteractive/incident-response-plan-template — Apache 2.0
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0 (sample code)
- https://github.com/vintasoftware/production-launch-checklist — MIT (pre-launch staged-gate framing)

**Star-threshold note:** Per the niche-specific direction (relax to ≥30 stars with disclosure), several sources are at or above ~180 stars; davidski/evaluator at 184 and voyage/open-autonomous-safety at 180 are well above the relaxed threshold. The ≥100-star convention used elsewhere in this seed set is met or exceeded by every cited source.

## Common patterns synthesized across sources

- **Loss as system-state, not component-failure.** A long-standing STAMP/STPA principle (MIT, academic, not used as a direct source per license) is restated as an original framing rule in skill 1 step 4. The wording — "the system [state] while [context]" — is original; the spirit is convergent across the broader functional-safety literature.
- **Four-question UCA structure.** Synthesized from the STPA tradition (academic, not cited) and rendered as an original structural rule in skill 1 step 6. The four cells (provided when shouldn't / not provided when should / wrong timing-order / wrong duration) are a well-known formulation; the skill states it directly without copying any single source's wording.
- **Four-category requirements derivation.** Skill 2's functional / performance / monitoring / fail-safe partition is original framing that synthesizes the spirit of the broader functional-safety practice — each constraint considered through every category, with explicit "inapplicable" rather than silent omission. The discipline of enforcing the consideration is sharper than what any single source articulates.
- **Allocation taxonomy with safety-rated vs. standard layer separation.** Skill 2 step 5 names the 10-layer allocation taxonomy as an original structural rule. The principle — that mixing layers reduces the chain to its weakest link — is convergent across functional-safety practice; the explicit ten-layer taxonomy is the skill's own.
- **Six-stage pre-deployment gate.** Skill 3's Stage 1-6 sequence is original synthesis. It borrows the gated-progression mindset from PagerDuty/counteractive/AWS incident-response patterns (which use stages for response, not pre-deployment) and the launch-checklist tradition from vintasoftware/production-launch-checklist (which uses checklists, not gated stages). The fusion — staged binary gates for pre-deployment safety — is the skill's own.
- **Kill-switch tested in production configuration, not on bench.** Skill 3 step 5 is an explicit rule; the convergent practice across operational sources informs the spirit, and the rule's statement is original.
- **Observer authority is named, not assumed.** Skill 3 step 6 makes "abort authority" an explicit property of each observer role; this is sharper than the implicit "anyone can stop a test" found in operational reviews.
- **Open-questions register as a first-class output.** All three skills produce explicit open-questions registers and treat them as the honest signal of analysis maturity. The discipline is original to this skill set; the spirit is convergent across operational and verification practice (the "known unknowns" tradition).
- **Mandatory disclaimer travels with extracts.** All three skills place the full disclaimer at head and foot of every output and repeat the no-PL/SIL/category-assignment caveat. This is the niche-specific defense.

## Rejections (sources considered but excluded)

- **stanislaw/awesome-safety-critical** (CC0, 1.6k stars). CC0 is in spirit more permissive than MIT but is not in the brief's allowlist (MIT/Apache/BSD/ISC/Unlicense). Excluded on a strict reading of the allowlist.
- **protontypes/awesome-robotic-tooling** (CC0). Same reason.
- **openregulatory/templates** (CC BY-NC-SA, 153 stars). NonCommercial clause blocks use on a marketplace; ShareAlike clause incompatible with the platform's licensing model. Hard reject. (This is a notable loss — the repo contains ISO 14971 risk-management templates that overlap meaningfully with the niche; the license excludes them.)
- **aliasrobotics/RSF** (Robot Security Framework) (GPLv3, 98 stars). Copyleft license; not in the allowlist. Also primarily security, not safety. Reject.
- **naivesystems/analyze** (GPLv3, ~193 stars). Copyleft; reject.
- **joelparkerhenderson/causal-analysis-based-on-system-theory** (CAST/STAMP/STPA documentation, ~75 stars). LICENSE file returned 404 on direct fetch and was not visible on the repository main page in the time available; without confirming the license is in the allowlist, **reject** per the brief's "verify; this niche is extremely sparse on permissive GitHub — disclose openly" instruction.
- **kiloreux/awesome-robotics** (6.6k stars, custom WTFPL-style permissive). The license is permissive in spirit but is a custom license, not one of the brief's named MIT/Apache/BSD/ISC/Unlicense. Reject on strict reading.
- **neka-nat/awesome-cobots** (21 stars, no license file visible). All-rights-reserved by default. Reject.
- **kaizen-nagoya/hazop** (license unclear). Reject.
- **dromation/open-fmea** (GPL 3.0). Reject.
- **cowboy2718/FMEA** (license unclear in time available). Reject.
- **GT-RAIL/carl_estop** (BSD — in allowlist), but content is a single ROS package for an E-stop UI for a specific lab robot; too narrow for methodology synthesis. Not used.
- **eugene-taylashev/risk_management** (MIT, 16 stars). Below relaxed ≥30-star threshold disclosed in the brief. Not used.
- **Safety-Critical-Rust-Consortium/safety-critical-rust-coding-guidelines** (license under Rust Foundation, mixed). Out of scope (Rust language coding guidelines; not hazard analysis or robot deployment review).
- **SCSC/GSN community standard** (scsc.uk/gsn, CC-BY 4.0). Not on GitHub and CC-BY not in the named allowlist. Reject.
- **commaai/openpilot, autoware, apollo** (large autonomous-driving stacks). Methodology is inside the stack as code, not as methodology documentation; not the right shape to synthesize from.

The rejections list is materially longer than the accepted list. Disclosure: the accepted sources are operational-safety adjacent (incident response, launch checklists, AV safety processes) rather than dedicated robot functional-safety repositories. The methodology in the three produced skills is original synthesis informed by the broader functional-safety practice (which is largely outside GitHub, in paywalled standards and academic publications that cannot be cited as sources under the brief's rules) and structured by the accepted MIT/Apache/MIT-0 sources for the operational discipline that surrounds the analysis.

## Originality and compliance

- All prose is original; no copied text from any cited or rejected source. The skills do not reproduce standards text from ISO 13849, IEC 61508, ISO 10218, ANSI R15.06, ISO 13482, or ISO 3691-4; the standards are named as the regimes the methodology is intended to align with, never quoted.
- No trademarked methodology names misused. HAZOP, STPA, STAMP, GSN, FAIR, ISO 26262 are referenced as named methodologies/standards; the skills do not claim to implement them, only to be structured for compatibility with them.
- The mandatory disclaimer is repeated verbatim in each skill's head and foot. The no-PL/SIL/category-assignment caveat is in the disclaimer and in the body. The deferral to "qualified safety engineer" and "notified-body assessment" is in every skill.
- The four-question UCA structure, the four-category requirements partition, the ten-layer allocation taxonomy, the six-stage pre-deployment gate sequence, and the open-questions register discipline are stated directly in original wording rather than borrowed from any source's specific formulation.

## Confidence

- **Skill 1 (Robot Hazard Analysis Conductor): medium-high on structure, medium on coverage claim.** The 12-move analysis produces an artifact with the right shape for downstream qualified-engineer refinement. The honesty of the output depends on the open-questions register being substantial; the skill is opinionated about this and the example demonstrates it. Main risks: the skill cannot replace a real STPA control-structure model (a graphical artifact requiring a tool); the four-question UCA enumeration is structural but not exhaustive; quantitative analyses (PL, SIL, category) are explicitly out of scope and the disclaimer enforces this.
- **Skill 2 (Safety Requirements Deriver): medium-high.** The derivation discipline (every constraint → four-category consideration → atomic requirements → allocation → verification sketch → integrity-target placeholder) is concrete enough that an evaluator can score whether the skill produced a structured set against an input. Main risks: garbage in, garbage out — if the upstream constraints are wrong, the requirements are wrong; allocation depends on architecture input and the open-questions register is the honest signal.
- **Skill 3 (Pre-Deployment Safety Review Designer): medium-high.** The 6-stage gated structure with explicit kill-switch protocol, observer authority, and post-deployment window is concrete and reviewable. Main risks: surrogates are imperfect; observer authority is exercised under social pressure; the close-out criteria for the post-deployment window are evidence-based but not a guarantee of latent-issue surfacing.
- **Overall niche confidence: medium.** Functional safety is a domain where the methodology guidance has to be both substantive and humble. The disclaimers, the no-PL/SIL/category boundary, and the explicit deferral to qualified engineers and notified bodies are the niche's specific defenses. The skills are useful as starting points for safety engineers and as discipline for development organizations; they are not useful as substitutes for either.

## Source-thinness — final note

The brief flagged this niche as extremely sparse on permissive GitHub. That flag was accurate. The bulk of the methodology that informs the three skills lives in paywalled standards and academic publications that cannot be cited as sources under the brief's MIT/Apache/BSD/ISC/Unlicense allowlist. The three skills produced are original synthesis; the cited sources contribute the operational discipline (gated reviews, observer protocols, severity language, kill-switch testing under representative conditions) that wraps the functional-safety analysis, not the analysis methodology itself. This disclosure is part of the skill set's honest accounting and is repeated here so the curation pipeline can decide whether the source-set is acceptable or whether the niche should be deferred until additional permissive sources emerge.
