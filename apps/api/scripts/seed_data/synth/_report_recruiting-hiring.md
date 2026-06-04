# Synthesis Report — HR (Recruiting & Hiring)

**Date:** 2026-05-14
**Curator:** skillsgit-curated
**Area:** HR — recruiting, sourcing, interviewing, hiring decisions, onboarding
**Niche slug:** `niche:recruiting-hiring`

## Files produced

1. `hr-job-description-author.skills.md` — drafts inclusive JDs from a role brief with anti-bias review.
2. `hr-interview-loop-designer.skills.md` — designs structured interview loops with signals, rubrics, calibration.
3. `hr-candidate-debrief-facilitator.skills.md` — facilitates calibrated debriefs and writes hire/decline rationale.
4. `hr-sourcing-message-crafter.skills.md` — writes evidence-anchored outreach to passive candidates.
5. `hr-new-hire-onboarding-planner.skills.md` — designs 30/60/90 plans with manager and mentor briefs.

All five are wave-2 originals with `license_type: free` and no pricing. Five skills (the upper end of the requested 3-5 range) were produced because each of the five canonical recruiting-hiring jobs is operationally distinct and merits its own methodology rather than being collapsed into a "hiring agent" skill.

## Sources per skill (URL-only, license re-verified)

All five skills share a substantially overlapping source set because the HR open-source landscape is thin and the canonical permissive-licensed handbooks each cover multiple stages. Sources used across skills:

- https://github.com/yangshun/tech-interview-handbook — MIT, ~140k stars, primary
- https://github.com/cockroachlabs/open-sourced-interview-process — CC0-1.0, 424 stars, primary
- https://github.com/sourcegraph/handbook — Apache-2.0, 180 stars, primary (archived 2024-07 but content is canonical)
- https://github.com/clef/handbook — CC0-1.0, 2.7k stars, primary
- https://github.com/hkdobrev/awesome-handbooks — CC0-1.0, 239 stars, meta-source (curated list of handbooks)
- https://github.com/sparksuite/employee-handbook — CC0-1.0, 56 stars, supplementary (sub-100 stars; used for handbook structure signal, not as primary methodology source)
- https://github.com/Assystant/SpotAxis — MIT, 32 stars, supplementary (sub-100 stars; used for ATS-flow signal on the recruiter side of the funnel)
- https://github.com/Paullyoung/NewRoleOnboardingPlan — CC0-1.0, 14 stars, supplementary on onboarding skill only (sub-100 stars; included because it is one of very few permissively-licensed 30/60/90 references on GitHub; methodology is industry-standard, the repo is a useful structural reference)

### Per-skill source list

- **Job Description Author (7 sources):** tech-interview-handbook, cockroachlabs, sourcegraph, awesome-handbooks, clef, sparksuite, SpotAxis.
- **Interview Loop Designer (7 sources):** cockroachlabs, sourcegraph, tech-interview-handbook, clef, awesome-handbooks, sparksuite, SpotAxis.
- **Candidate Debrief Facilitator (7 sources):** sourcegraph, cockroachlabs, tech-interview-handbook, clef, awesome-handbooks, sparksuite, SpotAxis.
- **Sourcing Message Crafter (6 sources):** cockroachlabs, sourcegraph, tech-interview-handbook, clef, awesome-handbooks, SpotAxis.
- **New Hire Onboarding Planner (6 sources):** Paullyoung/NewRoleOnboardingPlan, clef, sparksuite, sourcegraph, awesome-handbooks, cockroachlabs.

## Patterns identified across sources

1. **Structured interviewing converges on the same shape.** Across cockroachlabs, sourcegraph, and tech-interview-handbook, structured loops use predefined signals, anchored rubrics, independent scoring before debrief, and a recruiter-run debrief that walks signal-by-signal rather than interviewer-by-interviewer. The five-point or four-point scale (strong yes / yes / neutral / no / strong no) is shared across sources.
2. **Exercise-based assessment dominates over conversation-based assessment** at the more rigorous sources. CockroachLabs makes this explicit; the tech-interview-handbook reinforces it with extensive station-type guidance. Loops that are five behavioral interviews in a row are explicitly treated as worse than loops mixing station types.
3. **Anti-bias practices are operational, not theoretical.** The strongest recurring practices across sources are: independent scoring before any group discussion; two-rater coverage per signal; resume not shared with the technical panel; calibration sessions before launch and after the first three candidates. These appear in source after source as the highest-leverage practical moves.
4. **Job description craft is dominated by restraint, not enthusiasm.** Sources converge on: keep must-haves to fewer than seven items, prefer specific evidence anchors over years-of-experience proxies, separate "preferred" cleanly from "required", include explicit comp bands. Gendered and coded language is treated as a measurable problem with specific recurring offending words.
5. **Onboarding plans live or die on the manager's discipline.** Across sources (clef, sourcegraph, Paullyoung, sparksuite), the consistent finding is that ramp success is more correlated with the manager's discipline in running the 1:1s and feedback exchanges than with the formal plan structure. The 30/60/90 cadence is widely used but is treated as a scaffold, not a guarantee.
6. **Sourcing/outreach is the most under-documented area in permissively-licensed sources.** Most outreach guidance on the open web is commercial (HubSpot, LinkedIn, SeekOut) and not permissively licensed. The HR open-source landscape is thin here; the sourcing-message-crafter skill therefore relies on cross-application of message-craft patterns from outbound sales (already covered in the sales-cold-email-crafter skill, similar shape but explicitly distinct ethics around opt-out and personalization).
7. **Debrief is the weakest link in most loops.** Sources that describe debrief discipline well (sourcegraph being the clearest) treat it as a structural process with specific safeguards against anchoring, halo, recency, and affinity bias. Sources that treat debrief casually produce loops that look structured on paper but converge on the most senior voice in the room.

## Rejections (sources considered and not used)

- **ashishps1/awesome-behavioral-interviews** — GPL-3.0. Rejected per the MIT/Apache/BSD/ISC/CC0/Unlicense-only constraint. Verified via WebFetch.
- **mbianchidev/engineering-interviews** — AGPL-3.0. Rejected. Verified.
- **gregorojstersek/behavioral-interview-list-of-questions** — no LICENSE file declared. Rejected.
- **basecamp/handbook** — no LICENSE file declared. Rejected despite being a frequently cited reference; without a permissive license declaration the spec does not allow it as a source.
- **thiagooak/engineering-interview-grading-rubric** — no LICENSE file declared, 0 stars. Rejected.
- **handbook.gitlab.com / GitLab Handbook** — CC-BY-SA 4.0. Rejected as a primary source per the share-alike concern; widely cited as industry-standard for hiring practice but no GitLab-authored prose was reused. The general structural conventions are common to multiple permissively-licensed sources, so no functional gap.
- **MIT HR materials** — MIT-the-institution publishes hiring guidelines on hr.mit.edu, but the repository search collapses on the "MIT license" string. The institution's materials are not open-source licensed and were not used as sources.
- **Commercial blog content** (SeekOut, LinkedIn Talent Blog, Greenhouse, Lever, Workable, Karat, Metaview, LeadDev, etc.) — read for landscape signal during research but not cited as sources; these are not open-source code repositories. No prose used.
- **Templates and "interview rubric template" PDFs from vendor sites** — proprietary; not cited.
- **Trademarked methodology names** — kept generic. The 30/60/90 day plan is genericized; specific phrasings from Watkins' "The First 90 Days" are not reused. STAR (Situation/Task/Action/Result) is industry-standard vocabulary; treated as common knowledge, not as a methodology owned by any specific source.

## Source thinness disclosure (transparency)

The HR open-source landscape is materially thinner than the engineering or sales open-source landscape. Honest disclosures:

- **Only three sources cleanly exceed the 100-star threshold.** tech-interview-handbook (140k), clef/handbook (2.7k), cockroachlabs/open-sourced-interview-process (424). sourcegraph/handbook (180) and hkdobrev/awesome-handbooks (239) also exceed. The remaining sources (sparksuite 56, SpotAxis 32, Paullyoung 14) are sub-threshold and used as supplementary signal rather than as anchors. This is honestly disclosed per skill and is consistent with the wave-2 spec's allowance for sub-threshold sources where the niche's open-source pool is thin.
- **Three of the strongest commercial/industry references (GitLab Handbook, Basecamp handbook, ashishps1) are not usable.** GitLab is CC-BY-SA (share-alike risk); Basecamp has no declared license; ashishps1 is GPL-3.0. The strong methodologies these would have anchored (especially GitLab's hiring-process documentation) are covered by sourcegraph and cockroachlabs at a similar level of detail with permissive licensing.
- **The recruiter-outreach domain has the thinnest permissive open-source landscape.** Most authoritative guidance on sourcing message craft lives behind commercial publishers. The sourcing-message-crafter skill draws on permissively-licensed handbook material for the hiring-side context and on the wave-2 sales-cold-email-crafter skill's parallel methodology for the message-craft conventions (with HR-specific ethical adjustments around opt-out, similarity bias, and personalization restraint).
- **No source provides a debrief-specific methodology in depth.** Sourcegraph comes closest. The candidate-debrief-facilitator skill therefore synthesizes patterns from across multiple sources rather than anchoring on one; the methodology around naming disagreement, probing for gut feelings, and producing written rationale is constructed from converging signals across cockroachlabs, sourcegraph, and tech-interview-handbook with cross-application of structured-decision-making patterns from incident response and code review (also covered elsewhere in the synth corpus).

## Pricing rationale

Per spec: all skills set `license_type: free` and have no pricing. No pricing fields are populated.

## Confidence

**High** on overall fit and methodology coverage. The five skills cover the canonical recruiting-hiring funnel: write the JD, source candidates, design the loop, debrief, plan the ramp. Together they map cleanly to the operational workflow of a recruiter-plus-hiring-manager pair.

**High** on license compliance. All cited sources are MIT, Apache-2.0, or CC0-1.0. Each was re-verified via WebFetch. GPL/AGPL/CC-BY-SA sources were identified and rejected and are listed in the Rejections section.

**Medium** on star-threshold strictness. Three of eight cited repos meaningfully exceed 100 stars; two more sit between 100 and 500; three are sub-100 and are used as supplementary signal only. This is honestly disclosed per skill. The HR open-source landscape is thinner than engineering or sales; the disclosed sub-threshold usage is the best available rather than an oversight.

**High** on originality. All prose is original. No source repo's documentation, code, or templates are paraphrased; methodology is synthesized across multiple sources and rewritten in original language. Industry-standard vocabulary (30/60/90, STAR, strong yes / yes / no / strong no, structured interviewing) is used as common terminology rather than as branded methodology attribution.

**High** on trademark hygiene. Trademarked methodology names from books and consultancies (e.g., "The First 90 Days", "Topgrading", "Who: The A Method", "Predictive Index", "Culture Index", "Geeks and Geezers") are not used. Where their underlying ideas are common in the field (e.g., listening-before-acting in new-leader transitions), the ideas are reworked into original prose without naming the proprietary source.

**Medium** on freshness of patterns. Recruiting and hiring norms shift over multi-year cycles; the patterns synthesized are accurate as of the date in the changelog. Pay-transparency law in particular is changing quarter-by-quarter in 2024-2026; the JD skill flags this explicitly. The sourcing-message-crafter skill notes that filter sensitivity to certain phrasings shifts.

**Medium** on cross-jurisdiction applicability. The methodology is primarily calibrated to US and Western-European hiring norms. Some practices (independent scoring, anti-bias safeguards, debrief discipline) are universally applicable; others (specific anti-bias vocabulary lists, pay-transparency framing, comp-band conventions) are US-centric and are flagged as such where it matters.

## Follow-ups

- A wave-3 pass could add: `hr-reference-check-conductor` (structured reference calls with rubric-anchored questions); `hr-offer-negotiation-coach` (drafts offer-call framing, anticipates counter-asks); `hr-compensation-band-builder` (constructs internal comp bands from market data, levels, and equity logic). All three are operationally distinct from the five released here.
- A scoring-rubric-anchor library could be released as a paired data asset to the interview-loop-designer skill, with anchored rubric language for 12-15 common signals across role families. Treated as out of scope for this wave because anchor libraries require human review for trademark and consultancy attribution before publishing.
- The sourcing-message-crafter skill explicitly defers a multi-touch cadence to a future skill. Reasonable next addition would be `hr-sourcing-cadence-designer` with anti-creepy follow-up timing.
- The HR open-source landscape would benefit from a future curation pass that identifies recent additions (post-2024) under permissive licenses, especially in the debrief/decision-rationale and structured-reference-check spaces where current open-source coverage is thinnest.
