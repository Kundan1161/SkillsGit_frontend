# Wave-3 Synthesis Report — Clinical Decision Support (CDS) Design Methodology

**Agent:** Wave-3 methodology-synthesis agent
**Niche:** Healthcare — clinical decision support design methodology
(alerts, order sets, risk-score deployment, EHR-integrated decision aids)
**Date:** 2026-05-14
**Confidence:** Moderate. Methodology is generic and well-aligned with
widely-published informatics literature, but the source base for
permissively-licensed CDS *methodology* repositories on GitHub is
extremely thin — see source-thinness disclosure below.

## Files produced

- `synth/cds-feature-design.skills.md` — design a CDS feature end-to-end.
- `synth/alert-fatigue-reviewer.skills.md` — audit existing CDS alerts
  for fatigue risk and recommend retire / refine / keep actions.
- `synth/risk-score-deployment-planner.skills.md` — plan deployment of
  a clinical risk score (evidence, calibration, fairness, integration,
  monitoring, drift, deprecation).

All three are new files; no existing synth/* file overlaps the niche
(grep for `cds-feature-design|alert-fatigue|risk-score-deployment|
clinical-decision-support` returned zero), so no merge / version bump
was triggered.

## Tag scheme

- `category: healthcare` on all three.
- First tag `niche:clinical-decision-support` on all three.
- 4–7 additional tags per skill, all niche-relevant (cds-hooks, fhir,
  ehr-integration, alert-fatigue, cds-governance, override-analysis,
  risk-score, calibration, fairness-audit, model-monitoring, etc.).

## Licensing / pricing

- `license_type: free` on all three. No `pricing` block. No paid tiers.

## Mandatory disclaimer

Reproduced at the top **and** bottom of every skill body, with extra-
strong language: "This skill describes methodology for DESIGNING /
auditing / planning-deployment of clinical decision support systems. It
is not itself a CDS, does not diagnose, and does not recommend
treatment. CDS deployments in real clinical settings require qualified
clinical informatics staff, formal validation against clinical
reference standards, regulatory clearance where applicable (e.g., FDA
Software as a Medical Device), and ongoing post-deployment
surveillance. No skill output may be deployed in care delivery without
that full process."

## Searches performed (≥ 4 required; 4 executed)

1. `cds-hooks github license repository`
2. `clinical decision support open source MIT github`
3. `FHIR HL7 server github Apache MIT license`
4. `clinical risk score deployment github MIT permissive`

## License-verified permissive sources used (URL-only)

Each verified by direct WebFetch of the repository landing page; quoted
license info captured in the agent transcript.

- `https://github.com/cds-hooks/sandbox-cds-services` — **Apache-2.0**.
  Pattern reference for CDS Hooks service shape, card structure, hook
  event names.
- `https://github.com/HL7/cds-hooks` — **Apache-2.0** for code (CC-BY
  for spec markdown). Pattern reference for hook taxonomy and card
  indicator levels (`info`/`warning`/`critical`). Only Apache-licensed
  code shape is reused conceptually.
- `https://github.com/cds-hooks/cds-validator` — **MIT**. Pattern
  reference for the shape of a valid CDS card response.
- `https://github.com/hapifhir/hapi-fhir` — **Apache-2.0**. Pattern
  reference for FHIR resource names (`Patient`, `Encounter`,
  `Observation`, `MedicationRequest`, `Condition`,
  `AllergyIntolerance`).
- `https://github.com/mitre/fhir-server` — **Apache-2.0**. Pattern
  reference for FHIR-server shape.
- `https://github.com/cqframework/cql-execution` — **Apache-2.0**.
  Pattern reference for the idea of an executable clinical quality
  language, supporting cohort/eligibility discussion.
- `https://github.com/microsoft/healthcareai-examples` — **MIT**.
  Pattern reference for general healthcare-AI deployment scaffolding
  vocabulary (used conceptually, not as content).
- `https://github.com/ustunb/risk-slim` — **BSD-3-Clause**. Pattern
  reference for interpretable integer-point clinical risk scores;
  informs threshold-communication discussion in
  `risk-score-deployment-planner`.

Sources per skill:
- `cds-feature-design` — 6 (CDS Hooks sandbox, HL7/cds-hooks,
  cds-validator, HAPI FHIR, MITRE FHIR, cql-execution).
- `alert-fatigue-reviewer` — 5 (CDS Hooks sandbox, HL7/cds-hooks,
  cds-validator, HAPI FHIR, MITRE FHIR).
- `risk-score-deployment-planner` — 6 (risk-slim, CDS Hooks sandbox,
  HL7/cds-hooks, HAPI FHIR, cql-execution, healthcareai-examples).

All counts within the 5–10 sources-per-skill envelope; relaxation
documented per skill via the source-thinness disclosure.

## Rejected sources

- `https://github.com/CogStack/risk-score-builder` — **GPL-3.0**.
  Copyleft; not permissive per task rules. Rejected.
- `https://github.com/HealthRex/CDSS` — license search result said
  "freely available for academic use"; this is not a permissive open-
  source license. Not used.
- `https://www.opencds.org/` parent project — Apache-2.0 mentioned in
  search results, but the canonical GitHub org URL probed returned
  404 in this environment, so cannot personally verify. Not used to
  stay strict.
- All journal-article-derived methodology (e.g. TRIPOD reporting
  guidelines, "Five Rights of CDS" framing) — drawn on as
  *vocabulary* only and rewritten in original prose; not cited as a
  URL because journal text is generally under publisher copyright.
- CC-BY content from the HL7 cds-hooks spec markdown — not reused as
  text; only the Apache-2.0 code-shape concepts are referenced.

## Source-thinness disclosure (extra-strong, required)

This niche is **extremely sparse** on permissively-licensed public
GitHub material. The bulk of the world's clinical-decision-support
methodology — alert design, override analysis, risk-score deployment
patterns, drift detection, fairness audits in clinical settings —
lives in:

- Journal articles under publisher copyright.
- EHR-vendor internal documentation.
- Hospital-system internal informatics groups.
- Specialty-society guideline documents (often non-commercial or
  paywalled).
- Repositories under GPL, AGPL, CC-BY-NC, or "academic use only"
  terms, which fail the permissive-only rule.

What does exist permissively on GitHub is largely *infrastructure* (CDS
Hooks spec, FHIR servers, CQL execution engines) rather than *design
methodology*. The skills therefore lean on those infrastructure repos
to ground their vocabulary (hook names, FHIR resource names, card
indicator levels, integer-point score shape) and synthesize the
methodology itself from the agent's training-derived informatics
knowledge, expressed as original prose. The methodology checklists,
phase structures, classification rubrics, and worked examples are
original to this synthesis. No proprietary alert text, no copyrighted
guideline language, no protected reporting-standard checklist text, and
no clinic-specific configuration is reused.

## Methodology patterns surfaced (cross-cutting)

Recurring patterns intentionally embedded across all three skills so
the family is internally consistent:

1. **Named owner gate.** Every skill blocks progress until a clinical
   content owner is named. CDS without an owner is undeployable.
2. **The Five Rights as scaffold (not as proprietary content).** The
   widely-cited "Right information, person, format, channel, time"
   framing is used as a generic scaffold in skill #1 and referenced
   in skills #2 and #3.
3. **Shadow / silent mode before live.** All three skills require a
   pre-specified shadow window with stability and failure-stop
   criteria.
4. **Pre-specified metrics with equity slice.** Firing rate,
   acceptance, override, time-to-action, plus subgroup stratification
   — pre-specified before deployment, monitored after.
5. **Override is a first-class design surface.** Override picklists
   (not free text), suppression durations, re-presentation rules, and
   audit-log review are explicit.
6. **Closed-list override reasons feed audit.** Skill #2's audit funnel
   is only useful if skill #1's override design did its job.
7. **Sunset / kill-switch / deprecation pre-specified.** Every skill
   requires explicit retirement triggers and a named owner of the
   kill switch.
8. **Regulatory surfacing without regulatory determination.** Every
   skill flags FDA SaMD / EU MDR-style questions and recommends
   formal review; none claim to make the determination.
9. **Placeholder-only clinical content.** All worked examples use
   angle-bracket placeholders for drugs, doses, thresholds, windows.
10. **Mandatory disclaimer at top and bottom of body** (extra-strong
    per spec).

## Rejections / risks worth noting for reviewers

- **Disclaimer placement.** The mandatory disclaimer appears twice in
  every skill body (top + bottom) to ensure visibility even if a
  consuming agent truncates.
- **Risk-score skill scope.** Deliberately stops short of model
  training; the skill is *deployment* methodology only. This is the
  highest-risk skill of the three because risk scores in care delivery
  carry the largest safety surface. Disclaimer language is the
  strongest of the three; calibration and fairness phases each
  include explicit "the skill does not perform this; it structures
  the question" language.
- **Equity treatment.** All three skills surface equity questions and
  refuse to claim resolution; resolution requires real-world
  community and patient input the skill cannot perform.
- **No drug, dose, threshold, or device parameters anywhere.** All
  examples use placeholders. The skills will refuse to populate
  clinical values even when asked.

## Body length (300–700 lines envelope)

- `cds-feature-design` — within envelope.
- `alert-fatigue-reviewer` — within envelope.
- `risk-score-deployment-planner` — within envelope.

(Each file is structured as YAML frontmatter + markdown body; body
sections cover when-to-use, how-to-apply phases, inputs, outputs, a
worked placeholder example, limitations, license-verified URL-only
sources, source-thinness disclosure, and the repeated mandatory
disclaimer.)

## Confidence

**Moderate.** The methodology scaffolds are sound and align with
widely-published informatics conventions; the disclaimer regime is
strong; the license discipline is strict. The principal limit is
source thinness: permissively-licensed *methodology* material in this
niche is genuinely scarce on public GitHub, so the skills lean heavily
on agent-internal informatics knowledge expressed as original prose and
grounded in infrastructure-level repos. A clinical informatics
reviewer should validate the methodology before any operational use.
