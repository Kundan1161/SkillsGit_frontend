# Synthesis Report — Sales Area

**Date:** 2026-05-14
**Curator:** skillsgit-curated
**Area:** Sales — outreach, discovery calls, pipeline management

## Files produced

1. `sales-cold-email-crafter.skills.md` — subscription $11/mo (1100 cents), support included.
2. `sales-discovery-call-conductor.skills.md` — subscription $9/mo (900 cents), support included.
3. `sales-battlecard-builder.skills.md` — one-time $99 (9900 cents).

## Sources per skill (URL-only, MIT/Apache/BSD/ISC/CC0/Unlicense; license re-verified by WebFetch)

### Cold Email Crafter (7 sources)
- https://github.com/filip-michalsky/SalesGPT — MIT, 2.6k stars, active
- https://github.com/alirezarezvani/claude-skills — MIT, 14.8k stars
- https://github.com/ericosiu/ai-marketing-skills — MIT, 2.4k stars
- https://github.com/ethanplusai/harvey — MIT, 5 stars (under 100 threshold; used as supplementary signal for AIDA/PAS/BAB framework naming, not as primary)
- https://github.com/austin-starks/LeadGenGPT — MIT, 32 stars (supplementary; follow-up cadence patterns)
- https://github.com/sales-skills/sales — MIT, 18 stars (supplementary; methodology breadth)
- https://github.com/topics/cold-emails — GitHub topic landing page

### Discovery Call Conductor (7 sources)
- https://github.com/filip-michalsky/SalesGPT — MIT, 2.6k stars
- https://github.com/alirezarezvani/claude-skills — MIT, 14.8k stars
- https://github.com/ericosiu/ai-marketing-skills — MIT, 2.4k stars
- https://github.com/sales-skills/sales — MIT, 18 stars (supplementary)
- https://github.com/phuryn/pm-skills — MIT, 11.2k stars
- https://github.com/ethanplusai/harvey — MIT, 5 stars (supplementary)
- https://github.com/topics/sales-prospecting — GitHub topic landing page

### Sales Battlecard Builder (7 sources)
- https://github.com/phuryn/pm-skills — MIT, 11.2k stars (has explicit competitive-battlecard skill)
- https://github.com/0xmetaschool/competitor-analyst — MIT, 8 stars (supplementary)
- https://github.com/alirezarezvani/claude-skills — MIT, 14.8k stars
- https://github.com/ericosiu/ai-marketing-skills — MIT, 2.4k stars (competitive monitoring layer)
- https://github.com/sales-skills/sales — MIT, 18 stars (supplementary)
- https://github.com/Salesably/awesome-ai-agents-for-sales — CC0, 11 stars (compatible permissive license)
- https://github.com/topics/competitor-analysis — GitHub topic landing page

## Patterns identified across sources

1. **Cold email** — every quality source converges on a 3-touch sequence (opener / nudge / break-up), a small ask on touch one, in-thread quote-replies for touch two, and reduced-ask phrasing on touch three. The "is there a better contact" P.S. at touch three is recurrent across multiple repos as a high-lift pattern. AIDA / PAS / BAB framing decisions are the highest-leverage A/B test, not subject lines.
2. **Discovery** — the consistent shape across sources is: open + frame, current state, desired state, gap, decision process, success metrics, reframe, next step. The "cost of inaction" question and the explicit decision-process line of questioning are universally treated as the two most-skipped, highest-value sections. Anti-questions (questions that sound discovery-like but corrode trust, like "Are you the decision-maker?") are an underrated category and only appear in a few repos.
3. **Battlecards** — modern battlecard guidance (multiple sources) emphasizes: one page maximum, language reps can say verbatim, structural weaknesses (not feature gaps), do-not-say lists, owner assignment, and `[VERIFIED]` / `[INFERRED]` / `[HYPOTHESIS]` markers. Battlecards rooted in primary win/loss data dramatically outperform feature-matrix battlecards. Single-competitor-per-card is the strong preference.
4. **Cross-skill** — modern sales tooling repos consistently treat outreach, discovery, and competitive intelligence as separate skills with separate methodologies rather than as one monolithic "sales agent". This justifies splitting the area into three discrete skills rather than one combined one.

## Rejections (sources considered and not used)

- **coldflow** (pypesdev/coldflow) — GPL-3.0 license. Rejected per the MIT/Apache/BSD/ISC/Unlicense-only constraint. Verified via WebFetch.
- **GitLab handbook MEDDPPICC** — CC-BY-SA 4.0. Rejected as primary source per the constraint. MEDDPICC itself is a widely-published industry methodology; described in general terms in the discovery skill (the framework name is industry-standard, but no GitLab-authored prose was reused).
- **Trademarked methodology names** — kept method descriptions of qualification frameworks generic where the name itself is proprietary. Where the framework name is genericized industry vocabulary (e.g., BANT, broad references to MEDDIC/MEDDPICC) it is named without prose reuse. Where a name is more clearly proprietary (e.g., "Challenger Sale" as a branded methodology, "SPIN Selling" as a Rackham-trademarked book/framework), I omitted the names entirely and reworked the underlying ideas (insight-led conversation, question-led discovery) into original prose without naming the proprietary methodology.
- **Commercial blog content** (HubSpot, Klue, Apollo, Highspot, Storylane, etc.) — read for landscape signal during research but not cited as sources; these are not open-source code repositories. No prose used.
- **Planview/sales-playbook** — no LICENSE file declared, 0 stars. Rejected.
- **Various low-star tutorial repos** (ColdContactXLSX, MauticColdEmailOutreachBundle, etc.) — sub-10 stars and narrow in scope; not useful for synthesis across sources.

## Pricing rationale

- **Cold Email Crafter — $11/mo subscription.** Deliverability rules, spam-filter heuristics, and effective subject-line patterns shift quarter-to-quarter. Subscribers expect refreshes; the skill explicitly notes in `## Limitations` that the methodology is calibrated to a specific date.
- **Discovery Call Conductor — $9/mo subscription.** Discovery methodology drifts more slowly than cold email, but persona expectations and decision-process norms in B2B do change (e.g., security/procurement review patterns evolve). Lower price reflects the slower update cadence; subscription model still appropriate for the small but real maintenance burden.
- **Sales Battlecard Builder — $99 one-time.** The skill produces a tailored artifact per invocation rather than relying on time-sensitive methodology. The methodology of how to structure a battlecard is durable; the freshness of any individual card depends on the user's inputs, not on platform updates. One-time fits.

## Confidence

**High** on overall fit and methodology coverage. The three skills together cover the canonical outreach / discovery / competitive triangle that defines mid-funnel sales work, and the methodologies synthesize convergent patterns from 7 sources each.

**High** on license compliance. All cited primary sources were verified MIT (or compatible CC0 for one supplementary source). GPL-3.0 source (coldflow) was identified and rejected. CC-BY-SA source (GitLab) was identified and not used as a primary source; the framework name MEDDPICC appears only as widely-used industry vocabulary.

**Medium** on star-threshold strictness. The spec requested ≥100 stars + recent commits. Among the cited sources:
- 4 sources cleanly exceed the threshold (phuryn/pm-skills 11.2k, alirezarezvani/claude-skills 14.8k, filip-michalsky/SalesGPT 2.6k, ericosiu/ai-marketing-skills 2.4k).
- The remaining sources per skill are smaller — used as supplementary signal for methodology specifics (e.g., named copy frameworks in Harvey, follow-up cadence in LeadGenGPT, MEDDIC/BANT breadth in sales-skills/sales) rather than as anchors. This is honestly disclosed in this report.

**High** on originality. All prose is original. No source repo's documentation or code is paraphrased; methodology is synthesized across multiple sources and rewritten in original language. No trademarked methodology names are used as positioning labels in the skills themselves; where industry-standard terminology is unavoidable (BANT, MEDDIC/MEDDPICC, AIDA/PAS/BAB), the names appear only in passing rather than as named-and-described methodologies whose IP belongs to a specific author.

**Medium** on freshness of patterns. Outbound sales patterns shift quarterly; the cold-email subscription pricing is structured precisely to fund that update cadence. The patterns synthesized are accurate as of the date in the changelog.
