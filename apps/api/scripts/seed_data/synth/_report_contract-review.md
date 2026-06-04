# Wave-2 Synthesis Report — Legal / Contract Review

**Agent niche:** legal — contract review (NDA, MSA, SaaS terms, DPA, redlines, playbooks)
**Date:** 2026-05-14
**Author handle:** skillsgit-curated

---

## Files produced (4 skills)

All under `apps/api/scripts/seed_data/synth/`:

1. `legal-nda-triage-classifier.skills.md` — GREEN/YELLOW/RED inbound NDA screen.
2. `legal-msa-redline-helper.skills.md` — clause-by-clause MSA review with severity + fallbacks.
3. `legal-saas-terms-comparator.skills.md` — vendor SaaS terms vs customer standard, with calibrated data-profile gap analysis.
4. `legal-dpa-reviewer.skills.md` — GDPR Article 28 gap review with SCC / sub-processor / breach-notification mechanics.

No `nda-drafter` skill was produced. Drafting a balanced NDA from scratch via an LLM crosses a brighter line into apparent legal advice than the four review-oriented skills; the marginal value over the existing triage skill seemed low and the disclaimer surface area was harder to keep honest. Recommend a future pass with an explicit attorney-in-the-loop scaffold if drafting is wanted.

No existing legal skills were present in `synth/`, so all four are fresh creations — no merges or version bumps required.

Each skill has:

- `category: legal`
- First tag `niche:contract-review`
- 4–7 additional tags
- `license_type: free`, no pricing
- `## When to use` opening with an explicit non-legal-advice disclaimer
- Strong `## Limitations` section reiterating "not legal advice / engage counsel"
- Body length in the 300–700-line target range (largest is the DPA reviewer at ~340 lines, all written prose; no padding)

---

## Source survey — niche is genuinely thin

This niche is unusually source-poor under the allowlist (MIT / Apache-2.0 / BSD / ISC / Unlicense). The structural reason: legal-document publishers tend to use Creative Commons licenses (CC BY 4.0 for Common Paper and Bonterms; CC BY-ND 4.0 for Y Combinator SAFEs; CC0 for some curated lists) because attribution is the lever they want to preserve. CC-BY-* is **not in the allowlist** so those sources were excluded from primary methodology sourcing.

This was flagged transparently in every skill's `## Sources reviewed` section with a "**Source thinness disclosure**" paragraph.

### Sources used (accepted)

| Repo | License | Stars | Used for |
|---|---|---|---|
| https://github.com/Open-Source-Legal/OpenContracts | MIT | 1.3k | Annotation taxonomies, contract-review workflow mental model |
| https://github.com/accordproject/template-archive | Apache-2.0 | 344 | Composable-clause taxonomy, machine-readable contract structures |
| https://github.com/tollwerk/data-processing-agreements | Unlicense | 141 | Vendor DPA cataloging patterns, what real DPAs look like in practice |
| https://github.com/Ro5s/Startup-Starter-Pack | MIT | 112 | Document category coverage and startup-legal taxonomies |
| https://github.com/ankane/awesome-legal | CC0-1.0 | 957 | Curated index of permissive legal docs (CC0 is allowlist-equivalent public domain) |
| https://github.com/open-agreements/open-agreements | MIT (software) | 34 | Workflow methodology, contract-category enumeration. Template contents are CC-BY (excluded from methodology copy) |

In addition, two official statutory URLs were cited (not as methodology sources but as authoritative anchors):

- https://eur-lex.europa.eu/eli/reg/2016/679/oj — GDPR (DPA reviewer skill only)

Several repos have fewer than 100 stars — disclosed transparently. The thinness of this niche on GitHub made the >100 star bar impossible for all sources.

### Sources rejected (license or quality)

| Repo | Reason |
|---|---|
| https://github.com/CommonPaper/* | CC BY 4.0 template content — not in allowlist |
| https://github.com/Bonterms/Mutual-NDA (and other Bonterms repos) | CC BY 4.0 — not in allowlist |
| https://github.com/SixArm/consulting-agreement | CC-BY-SA / GPL-2.0 / GPL-3.0 — GPL family not in allowlist; CC-BY-SA not in allowlist |
| https://github.com/cure53/Contracts | No license file detected — must reject |
| https://github.com/ahmetkumass/contract-analyzer | License not specified |
| https://github.com/bitmovin/unda | License unverified and only 29 stars — caution |
| https://github.com/NDAify/ndaify-templates | MIT but 0 stars and content tracks Waypoint NDA (Kyle Mitchell, separately licensed); excluded out of caution |
| https://github.com/mgifford/non-disclosure-agreements | License unverified |
| https://github.com/jackmorgan/the-plain-contract | Not investigated due to early sufficiency |
| https://github.com/customer-terms/* (GitHub's own DPA) | Microsoft proprietary terms — not in allowlist |

Common Paper and Bonterms are referenced **conceptually** in industry context (the agent knows they exist as market standards), but no clause text, drafting language, or structural copy was taken from them, and they are not cited in `## Sources reviewed`. Skill methodology was synthesized from workflow patterns described in the MIT-licensed tools above, plus the agent's training-data knowledge of how contract review is taught and practiced in-house.

---

## Methodology patterns identified across sources

A few recurring patterns shaped the methodology of all four skills:

1. **Triage-before-review.** Open-source legal tooling (OpenContracts annotation flow, the open-agreements pipeline) consistently treats document intake as a classify-then-route step rather than a uniform deep review. The NDA triage skill is the cleanest expression; the SaaS comparator and DPA reviewer also use a meets/partial/fails verdict ladder to support intake-style routing.

2. **Clause-by-clause structure beats holistic.** Workflow tools assume a structured clause taxonomy (Accord Project's clause types; OpenContracts' label schemas). Each skill therefore enumerates load-bearing clauses by name and assesses each independently, rather than producing a "looks balanced" gloss.

3. **Calibration via deal/data context.** The same clause is acceptable on a $50K analytics deal and unacceptable on a HIPAA EHR deal. Three of the four skills take a `deal_context` or `data_profile` input that calibrates severity, mirroring the way real vendor-risk workflows attach data-classification metadata to contract review.

4. **Must-have / walk-away separation.** The MSA redline skill's must-have vs nice-to-have distinction is the practical leverage point — uncalibrated flag-everything reviews stall negotiation. This pattern shows up in the awesome-legal curation philosophy and in OpenContracts' "annotate the load-bearing claim" framing.

5. **Out-of-scope acknowledgment.** Every skill explicitly lists what was not reviewed (annexes, sub-processor diligence, security exhibit, TOMs, jurisdictional regulatory analysis). Silent skipping is a malpractice pattern in human reviewers too; making the skip explicit is half the value.

---

## Confidence

**Medium-high** for the methodology faithful to in-house contract-review practice. **Medium** for source sufficiency — the allowlist made primary GitHub sourcing thinner than usual, and the skills lean more heavily on the agent's training knowledge of contract-review practice as taught in-house and in legal-ops circles than on direct repo synthesis. This is disclosed in every skill's source section.

**Lower** for any output read as substantive legal guidance — every skill has been written to constantly remind the user that the output is a worklist, not advice, and to route to a qualified attorney. Defensible if read as triage tooling; not defensible if read as a substitute for counsel. The disclaimer architecture is the most important feature, not an afterthought.

---

## Legally-adjacent flags worth surfacing to platform owners

- **Unauthorized practice of law (UPL).** Distributing skills that classify, redline, and recommend on contracts raises UPL questions in some US states (notably California, New York, Texas) and in some non-US jurisdictions. The disclaimer architecture I built is the minimum mitigation; platform-level review by counsel admitted in target jurisdictions is recommended before any marketplace listing in those geographies. Consider an additional click-through disclaimer at install time for skills under `category: legal`.
- **Attorney-client privilege.** Outputs from these skills are *not* privileged. A buyer using one of these skills and saving the output into a record system may create discoverable communications. Worth surfacing in the skill listing UI as a caveat, ideally above the install button.
- **Cross-jurisdiction methodology.** The DPA reviewer is GDPR-anchored. Buyers in non-EEA jurisdictions may misapply it. Consider whether the marketplace UI should surface a "designed for [framework]" tag at the listing level beyond the existing tags.
- **Industry-specific frameworks.** HIPAA BAA, financial-services regulatory addenda, defense / ITAR clauses, life-sciences trial agreements all sit adjacent to contract review and were *not* covered. They each require specialist methodology — recommend a future wave with explicit industry scoping rather than expanding the generic skills.
- **Model-training on customer data.** I added explicit AI-clause handling in the MSA and SaaS comparator skills as a 2026-current concern; market norms are still moving and these skills will need periodic refresh as case law and supervisory guidance evolve.

---

## Follow-ups recommended

1. **Add a click-through disclaimer at install for `category: legal` skills.** The skill body disclaimers are necessary but the install UX should reinforce them.
2. **Consider a `nda-drafter` skill only with an explicit attorney-in-the-loop scaffold** (i.e., the skill produces a draft and explicitly routes it through a named human reviewer before any output can be exported). Drafting carries materially more UPL exposure than reviewing.
3. **Specialist wave for regulated industries.** HIPAA BAA, FedRAMP supplemental terms, ISDA master agreement reviewer, life-sciences clinical-trial agreements. Each is its own framework.
4. **DPA reviewer companion for non-GDPR frameworks.** CCPA service-provider terms, LGPD operator terms, India DPDP, China PIPL cross-border review. Worth their own skills rather than one polyglot DPA reviewer.
5. **Refresh cadence.** Data-protection law and AI-clause norms are moving fast enough that these skills should be reviewed at least annually. Build a refresh hook into the curation calendar.
6. **Allowlist reconsideration.** If CC-BY-4.0 (attribution-only, no share-alike) sources were admitted with mandatory attribution in `## Sources reviewed`, the methodology base for legal skills would roughly quadruple (Common Paper, Bonterms, several lawyer-published Markdown collections). Worth a policy review by platform legal — CC-BY-4.0 is widely considered enterprise-safe with attribution, and excluding it forces a thinner methodology in legal/policy/governance niches than the underlying skill quality requires.
