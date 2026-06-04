# Wave-2 synthesis report — operations / change management & rollouts

## Files produced

- `synth/ops-rollout-plan-author.skills.md`
- `synth/ops-change-impact-assessor.skills.md`
- `synth/ops-release-communication-author.skills.md`
- `synth/ops-kill-switch-designer.skills.md`

Four skills produced (no merges — existing synth contains no overlapping skills in this niche; the grep matches in earlier files were incidental keyword uses, not methodological overlap).

## Sources surveyed (license verified, allowlist-compliant)

| Repo | License | Stars | Used in |
| --- | --- | --- | --- |
| argoproj/argo-rollouts | Apache-2.0 | ~3.5k | all 4 |
| fluxcd/flagger | Apache-2.0 | ~5.3k | rollout-plan, impact, kill-switch |
| Unleash/unleash | Apache-2.0 | ~13.5k | all 4 |
| flagsmith/flagsmith | BSD-3-Clause | ~6.4k | rollout-plan, impact, kill-switch |
| reactjs/rfcs | MIT | ~5.8k | rollout-plan, impact, release-comms, kill-switch |
| concourse/rfcs | Apache-2.0 | ~57 | rollout-plan, impact |
| vintasoftware/production-launch-checklist | MIT | ~16 | all 4 (low stars — used for launch checklist patterns) |
| thoughtbot/templates | MIT | ~76 | rollout-plan, release-comms (RELEASING template) |
| release-drafter/release-drafter | ISC | ~3.9k | release-comms, kill-switch |
| release-notes/release-notes-spec | MIT | ~8 | release-comms (low stars — schema reference only) |

## Sources rejected

- **SkeltonThatcher/run-book-template** — CC BY-SA 4.0. Not in allowed-license list; excluded though it is widely cited for deployment runbook patterns.
- **LaunchDarkly/featureflags** — no license file (archived). Excluded; was potentially the most directly relevant guide.
- **GitLab Handbook (rollout plans, change management, organizational change management)** — CC BY-SA 4.0. Excluded as a citable source despite being one of the strongest publicly available references on this topic.
- **Berkeley HR Change Management Toolkit** — university work, license unclear, not GitHub. Excluded.
- **kieranpotts/rfcs** — CC0-1.0 (public domain, fine to cite) but only 1 star and largely duplicative of reactjs/rfcs which has stronger signal; not cited.
- **acalub/killswitch** — small utility repo (low stars, license unclear from snippet); not cited.

## Sources per skill

**ops-rollout-plan-author** — 8 sources: argo-rollouts, flagger, unleash, flagsmith, vinta launch checklist, thoughtbot templates, reactjs rfcs, concourse rfcs.

**ops-change-impact-assessor** — 7 sources: argo-rollouts, flagger, unleash, flagsmith, reactjs rfcs, concourse rfcs, vinta launch checklist.

**ops-release-communication-author** — 8 sources: release-drafter, release-notes-spec, thoughtbot templates, vinta launch checklist, argo-rollouts, unleash, flagsmith, reactjs rfcs.

**ops-kill-switch-designer** — 7 sources: unleash, flagsmith, argo-rollouts, flagger, release-drafter, vinta launch checklist, reactjs rfcs.

All within the 5–10 sources/skill range.

## Patterns abstracted

Across the verified open-source corpus and the niche's general practitioner literature, the following methodological patterns recur and were synthesized into original prose (no copying):

1. **Phase shapes are categorical.** Real rollouts are not freeform — they fall into pilot→expansion→GA, canary→ramp→100%, cohort waves, or dual-run→cutover. Mixing shapes by accident is the rollout-planning antipattern; naming the shape is half the discipline. (Drawn from argo-rollouts, flagger, vinta launch checklist conceptual structure.)
2. **Exit criteria are observable, not date-based.** Progressive-delivery platforms enforce metric-based gates between rollout steps; the same discipline applies to organizational rollouts. Dates are estimates; exit criteria are commitments.
3. **Abort criteria precede activation.** Every progressive delivery framework (argo-rollouts, flagger, unleash) builds abort-on-analysis into the model. The skill carries this pattern into both technical and organizational rollouts: the abort question is answered before ship.
4. **Friction has multiple categories.** Behavior change, system change, identity change, incentive change. Mitigation differs by category — bundling them produces a uniform "needs training" recommendation that does not address incentive flips or identity loss.
5. **Authority to flip is delegated low.** Kill switches behind high-process approval do not get flipped at 2am; the consistent open-source pattern (unleash, flagsmith) is RBAC with operator-level authority to disable.
6. **Comms are pre-written and channel-specific.** Release-drafter and release-notes-spec both encode channel-specific outputs; the skill extends this principle to internal, customer, in-app, sales, and support channels with different jobs each.
7. **Recovery is a separate decision from rollback.** Flipping the switch back is a different event from flipping it; the recovery rollout is itself a (smaller, sharper) rollout.
8. **Risk register: severity × likelihood × mitigation × owner.** RFC and RFC-adjacent processes (reactjs/rfcs, concourse/rfcs) use a "drawbacks and alternatives" structure that maps to a risk register; the skill operationalizes it.

## Honesty about the niche

The user's note was correct: business-side organizational change management (executive sponsorship, stakeholder alignment, training-focused models) is **sparse** on permissively-licensed GitHub. The strongest sources are technical (progressive delivery, feature flags, release tooling) plus a small set of MIT-licensed launch checklists. GitLab's handbook is the strongest organizational-change reference but is CC BY-SA 4.0 and excluded.

To compensate, the four skills lean into the **technical-rollout-as-discipline** framing and explicitly extend its patterns (phased exit criteria, abort thresholds, kill switches, instrumented telemetry) to organizational changes that lack natural rollback. The change-impact-assessor and rollout-plan-author skills are the most general-knowledge-influenced of the four; I have flagged this honestly here. The release-communication-author and kill-switch-designer skills are well-supported by the technical-rollout open-source corpus.

## Confidence

- **rollout-plan-author** — Medium-high. The phase-shape taxonomy is a clean synthesis; the "exit criteria not dates" rule is well-supported by the progressive-delivery corpus and reflects field practice. Risks: the org-change side of the framing leans on general knowledge.
- **change-impact-assessor** — Medium. The four-category friction decomposition is the skill's most opinionated and most general-knowledge-supported claim. The risk-register structure is well-supported. Risks: the audience-discovery probing is heuristic and depends on the model surfacing audiences the proposer omitted.
- **release-communication-author** — High. Multi-channel comms with channel-specific jobs is concretely supported by release-drafter, release-notes-spec, and thoughtbot templates. The "lede before excitement" rule and the calendar-based dispatch are field-tested patterns.
- **kill-switch-designer** — High. This is the most directly-supported skill. The progressive-delivery and feature-flag corpus encode every element (mechanism, triggers, authority, comms, recovery) explicitly. The org-change extension is light here; this skill is squarely technical.

## Follow-ups / spawnable tasks

1. Consider a fifth skill `change-objection-handler` (was optional in the brief; deferred because the four shipped cover the main job-to-be-done and a fifth would dilute the niche). If demand emerges, it would consume stakeholder-friction frameworks; sourcing would be thin.
2. The rollout-plan-author currently leans on cohort-waves as the default for non-technical rollouts. A future version could specialize for specific change classes (CRM migration, performance-review-process change, pricing change, M&A integration) — each has its own dominant patterns.
3. The kill-switch-designer's "must build before ship" telemetry checklist could become a standalone skill (telemetry-readiness reviewer) if the appetite exists.
4. Worth verifying with the validator: line counts on each skill are in the 300-700 range (rollout-plan ~440, impact-assessor ~330, release-comms ~430, kill-switch ~390); please confirm during the integration pass.
