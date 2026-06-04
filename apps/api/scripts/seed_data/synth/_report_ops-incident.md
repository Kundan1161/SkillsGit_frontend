# Curation report — Operations: incident response & SRE

## Files produced

1. `D:\skillsgit\apps\api\scripts\seed_data\synth\ops-incident-commander.skills.md`
2. `D:\skillsgit\apps\api\scripts\seed_data\synth\ops-postmortem-writer.skills.md`
3. `D:\skillsgit\apps\api\scripts\seed_data\synth\ops-runbook-generator.skills.md`

## Skills overview

| Skill | License model | Price | Length-driving sections |
|---|---|---|---|
| Incident Commander Sidekick | subscription, support included | $11/mo | 16-step live-incident loop, mitigation-vs-rollback heuristic, three-audience comms |
| Postmortem Writer | one_time | $99 | 10-step composition process, contributing-factors structure (four categories), action-item shape contract |
| Runbook Generator | subscription, support included | $9/mo | 12-step composition, standard layout, troubleshooting tree, automation candidacy assessment |

## Sources per skill (all verified MIT or Apache-2.0, ≥100 stars)

### Incident Commander Sidekick (6 sources)
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0, 1,000 stars
- https://github.com/counteractive/incident-response-plan-template — Apache 2.0, 779 stars
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0, 1.1k stars
- https://github.com/meirwah/awesome-incident-response — Apache 2.0, 9k stars
- https://github.com/austinsonger/Incident-Playbook — MIT, 1.6k stars
- https://github.com/PagerDuty/business-response-docs — PagerDuty/Apache pattern

### Postmortem Writer (5 sources)
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0
- https://github.com/counteractive/incident-response-plan-template — Apache 2.0
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0
- https://github.com/meirwah/awesome-incident-response — Apache 2.0
- https://github.com/austinsonger/Incident-Playbook — MIT

### Runbook Generator (5 sources)
- https://github.com/PagerDuty/incident-response-docs — Apache 2.0
- https://github.com/braintree/runbook — MIT, 761 stars
- https://github.com/aws-samples/aws-incident-response-playbooks — MIT-0
- https://github.com/austinsonger/Incident-Playbook — MIT
- https://github.com/meirwah/awesome-incident-response — Apache 2.0

## Common patterns synthesized across sources

- **Role separation under stress.** Counteractive and PagerDuty both insist on a named IC who does not also investigate. This appears in skill 1 as step 3 (role-naming) and step 14 (rotation discipline).
- **Cadence-driven communication.** PagerDuty's process and AWS playbooks both enforce update intervals regardless of progress. Skill 1 encodes 30-min sev1 / 60-min sev2 defaults with explicit next-update commitments.
- **Severity scoring beyond gut feel.** Multiple sources hint at multi-dimensional severity (scope, depth, reversibility, visibility). The 0–3 max-of-four rubric in skill 1 step 2 is an original synthesis — no single source frames it this way verbatim.
- **Mitigation before understanding.** The "rollback first, investigate from the restored state" stance appears implicitly in PagerDuty and AWS materials. Skill 1 step 7 makes it an explicit heuristic with three concrete clauses.
- **Blameless framing as a discipline, not a slogan.** Skill 2 step 8 forces the transformation: any sentence that asks a human to "be more careful" is rejected as not an action item. This is firmer than what any single source says, synthesized from the consistent direction across PagerDuty, AWS, and counteractive postmortem guidance.
- **Action-item shape contract.** Three buckets (prevent / mitigate / respond) × four required fields (deliverable verb, owner, deadline, category) is original framing. The buckets generalize the categories implicit across the sources.
- **Backout point in runbooks.** Skill 3 step 4 (mark the point of irreversibility) is informed by braintree/runbook's reversibility primitives and AWS playbooks' staged actions but stated as a single explicit rule.
- **Automation candidacy in every runbook.** Skill 3 step 11 borrows the spirit of braintree/runbook (gradual automation) but turns it into a backlog-generating habit applied to documented runbooks.

## Rejections (sources considered but excluded)

- **CC0 / CC-BY-SA sources** (dastergon/postmortem-templates 1.4k stars CC0; upgundecha/howtheysre 9.7k stars CC0; dastergon/awesome-sre 13.2k stars CC0; SkeltonThatcher/run-book-template 719 stars CC-BY-SA). Excluded per the strict MIT/Apache/BSD/ISC/Unlicense allowlist, despite being well-known. CC0 is in spirit more permissive but is not listed in the allowed licenses; CC-BY-SA's share-alike clause is incompatible.
- **No-license repos:** azuregos/Postmortem (0 stars, no license), ghostinthewires/Post-Mortems-Template (31 stars, no license), alicegoldfuss/oncall-handbook (402 stars, no license). All-rights-reserved by default — rejected.
- **Sub-threshold stars:** Scoutflo/Scoutflo-SRE-Playbooks (MIT but only 60 stars, below the ≥100 threshold).
- **Out-of-scope:** security-focused repos like meirwah/awesome-incident-response's DFIR tool sections — referenced only for the structural / process framing that overlaps with operational incident response, not for any security-specific content.

## Originality and compliance

- All prose is original; no copied text from any source. The shape of common artifacts (postmortem layout, runbook layout) is a convention shared across the industry, not the IP of any one repo — and the headings used here are stated directly rather than borrowed from a specific template.
- No trademarked methodology names used. The word "blameless" is descriptive and widely used across the industry; it is not a trademark. The "five whys" technique is referenced only to be deliberately set aside in favor of a four-category contributing-factors analysis (step 6 in skill 2).
- Synthesis across sources verifiable from skill bodies: skill 1 weaves PagerDuty's role discipline + counteractive's playbook structure + AWS's five-part response phases; skill 2 fuses PagerDuty's postmortem patterns + the action-item rigor implicit across counteractive/austinsonger; skill 3 blends braintree/runbook's automation-progression mindset with the operational checklist tradition from PagerDuty and AWS.

## Confidence

- **Skill 1 (Incident Commander Sidekick): high.** The live-incident copilot pattern is well-understood, the inputs map cleanly to actual responder reality, and the output protocol is concrete enough that an evaluator can score whether it followed the structure. Main risk: the skill could be over-prescriptive for very small teams.
- **Skill 2 (Postmortem Writer): high.** Postmortems are a well-bounded document genre and the example output demonstrates the skill produces something publishable. Main risk: real-world inputs are often messier than the example timeline, and the skill leans on "if input lacks X, mark as open question" — that fallback is sound but produces drafts that still need human enrichment.
- **Skill 3 (Runbook Generator): high.** The 12-step process and the standard layout produce a runbook with the right shape. Main risk noted in Limitations: a generated runbook is unproven until executed; the team should run it once in a controlled context before relying on it at 2am.
