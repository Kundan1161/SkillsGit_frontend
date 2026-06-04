# Wave-3 Synthesis Report — Biotech / Regulatory Submission Methodology

**Niche:** Biotech — regulatory submission methodology (FDA 510(k), IND/NDA, BLA, EMA, eCTD modules)
**Agent slug:** `niche:regulatory-submission`
**Date:** 2026-05-14

## Files produced

All produced under `D:/skillsgit/synth/` (the task instructions specified `synth/<slug>.skills.md`; existing seed-data synth lives at `apps/api/scripts/seed_data/synth/` but did not contain any biotech/regulatory entries, so no merge or version bump was needed).

1. `synth/submission-strategy-planner.skills.md` — methodology for classifying a product against FDA/EMA/ICH pathways, picking the right route (510(k) vs De Novo vs PMA; traditional IND vs investigator-initiated; 505(b)(1) vs 505(b)(2) vs ANDA; BLA vs biosimilar 351(k); CE marking pathway), and building a milestone plan anchored on the rate-limiting work stream with pre-submission interactions as planning rocks.
2. `synth/predicate-comparison-architect.skills.md` — methodology for structuring the substantial-equivalence argument in a 510(k): four-corner predicate eligibility test, intended-use vs indications-for-use vs technological-characteristics vs performance comparison tables, split-predicate guidance, bridging-evidence mapping, NSE-risk scoring, and the explicit recommendation to switch to De Novo when SE is being strained.
3. `synth/clinical-evidence-narrative.skills.md` — methodology for drafting the clinical-evidence narrative in Module 2.5/2.7, 510(k) clinical sections, De Novo and PMA clinical evidence, and EMA CER: claim-anchored study-design adequacy, endpoint relevance, statistical-power and effect-size honesty, subgroup/sensitivity treatment, integrated safety, and explicit fully/partially/unsupported gap analysis vs the proposed label.

I produced **three** skills rather than four. The optional fourth (`submission-gap-reviewer`) would have substantially overlapped with the clinical-evidence narrative gap-analysis section and the strategy planner's risk register. Three skills with deep methodology serve the niche better than four with thinner separation — and the source-thinness in this niche (see below) argues against stretching the methodology over more skills than the evidence base supports.

## Existing-skills check (merge analysis)

I scanned `apps/api/scripts/seed_data/synth/` for biotech/regulatory entries with `grep -iE "biotech|regulatory|fda|510|clinical|submission|ind|pharma|medical"`. **No matches.** This niche is uncovered in the existing catalog, so no version bumps or merges were performed. All three skills are fresh `version: 1.0.0`.

## Sources reviewed and licenses verified (per-skill 5-7 each, URL-only)

**Verified MIT / permissive (used as legitimate methodology references):**

- `https://github.com/innolitics/rdm` — **MIT** (verified via badge + LICENSE.txt). Regulatory documentation manager for medical-device software (62304, 14971, 510(k)).
- `https://github.com/rlwadh/fda-predicate-finder` — **MIT** (verified via badge + README footer). Predicate device search tool for 510(k).
- `https://github.com/arnaud-dg/fda-510k` — **MIT** (verified via README declaration). RAG knowledge base over 510(k) documents.
- `https://github.com/tsbischof/fda` — **BSD-2-Clause** (verified via GitHub navigation). 510(k) scraper and predicate analysis tooling.
- `https://github.com/awconway/spiritR` — **MIT** (verified via DESCRIPTION file `License: MIT + file LICENSE`). SPIRIT-checklist R Markdown template for clinical trial protocols.

**Verified excluded (non-permissive):**

- `https://github.com/openregulatory/templates` — **CC BY-NC-SA 4.0**. NonCommercial clause disqualifies it from a marketplace context. Excluded.
- `https://github.com/dayzero/ectd_indexer` — **GPL-3.0**. Copyleft excluded per the MIT/Apache/BSD/ISC/Unlicense-only rule.
- `https://github.com/virtalabs/tapirx` — **GPL-3.0**. Excluded.
- `https://github.com/RConsortium/submissions-pilot2-to-fda`, `https://github.com/RConsortium/submissions-pilot1-to-fda`, `https://github.com/elong0527/ectddemo` — **no LICENSE file detected** during verification. Excluded (no license = all rights reserved).

**Regulator-public-domain references (cited as URLs only, never copied):**

- `https://www.fda.gov/regulatory-information/search-fda-guidance-documents` — FDA guidance index.
- `https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-notification-510k` — FDA 510(k) overview.
- `https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request` — FDA De Novo overview.
- `https://www.fda.gov/regulatory-information/search-fda-guidance-documents/format-traditional-and-abbreviated-510ks` — FDA 510(k) format guidance.
- `https://www.ema.europa.eu/en/human-regulatory-overview` — EMA human-medicines regulatory overview.
- `https://www.ema.europa.eu/en/human-regulatory-overview/research-and-development/scientific-guidelines` — EMA scientific guidelines.
- `https://www.ich.org/page/efficacy-guidelines` — ICH efficacy guideline index (E6, E8, E9, E10).

## Patterns identified across sources

1. **Documentation-as-code structure** (innolitics/rdm) — regulatory documentation managed as Markdown in git with traceability between requirements, design, risk, and test. The pattern generalizes well to the planner and gap-analyzer methodology even where the source repo's scope is narrower (62304/14971/510(k) for software).
2. **Predicate-as-database pattern** (rlwadh, tsbischof, arnaud-dg) — three independent MIT/BSD repos treat the 510(k) predicate landscape as a queryable corpus. The shared insight is that predicate strategy is fundamentally an information-retrieval problem layered with an argument-construction problem. The `predicate-comparison-architect` skill encodes the argument layer; the retrieval layer is left to the sponsor's database access.
3. **SPIRIT-aligned protocol structure** (awconway/spiritR) — even though this skill works post-trial rather than at protocol drafting, the SPIRIT taxonomy (population, intervention, comparator, outcome, follow-up, statistical plan) maps cleanly to the claim-vs-evidence audit that the clinical-evidence narrative skill performs.
4. **Backward-mapping from submission contents** — every reviewed tooling repo organizes content around the submission's required output, not the sponsor's internal workflow. The strategy planner's "map work product backwards from Module contents" step is the methodology version of this pattern.

## Rejections and why

- **Promotional or commercial-vendor blog content** — surfaced repeatedly in search (Greenlight Guru, Ketryx, MedCrypt). Not used as primary methodology sources because they are not GitHub repos under permissive licenses; their content is marketing rather than open methodology, and copying would create both license and authenticity problems. I did not cite them.
- **CC BY-NC-SA OpenRegulatory templates** — explicitly excluded by the MIT/Apache/BSD/ISC/Unlicense-only rule. This was a significant source-thinness driver; OpenRegulatory's catalog is otherwise excellent.
- **GPL-licensed eCTD tooling (dayzero, tapirx)** — excluded by the permissive-only rule.
- **RConsortium and ectddemo repos** — no LICENSE file detected during verification; excluded under the all-rights-reserved-by-default rule. These would be high-quality additions if a permissive license is added.
- **An optional fourth skill (`submission-gap-reviewer`)** — declined for depth-vs-breadth reasons. The clinical-evidence narrative skill's gap-analysis section and the strategy planner's risk register cover most of what a gap-reviewer would do. A standalone gap-reviewer would either duplicate or be too thin on its own evidence base.

## Honest disclosure of source thinness

This niche is **extremely sparse on permissively-licensed GitHub repositories.** The reasons are structural:

- Most rigorous regulatory tooling is produced inside regulated companies and never open-sourced because it would expose proprietary controlled documents and quality-system content.
- The most-cited open templates (OpenRegulatory's ISO/IEC templates, Common Paper's contract templates) are deliberately CC-licensed for attribution and share-alike, which excludes them from a marketplace synthesis.
- FDA, EMA, ICH, MHRA, and other regulators publish authoritative methodology in public-domain form, but the format is dense guidance documents — not GitHub repositories — and the guidance is what is being paraphrased durably across the field.
- The R Consortium pilot submissions are exemplary work but have not (at verification time) attached licenses to the submissions-pilot repositories themselves, which makes them unusable as sources here.

The methodology in all three skills is therefore grounded in:

1. The five verified MIT/BSD permissive GitHub repos (relatively narrow corpus — three of them focus on 510(k) predicate discovery, one on software-device documentation, one on SPIRIT protocol templates).
2. URL-only references to regulator-public-domain guidance documents (FDA, EMA, ICH) — used to anchor terminology and pathway names, **not** copied as source text.
3. Durable, widely-known methodology that has been industry common knowledge for decades (predicate comparison, substantial equivalence reasoning, ICH M4 CTD structure, ICH E9 statistical principles, SPIRIT/CONSORT-style trial reporting structure).

I have flagged this thinness transparently in the `## Sources reviewed` section of each skill body, called out specifically which industry templates were excluded and why (CC-NC and GPL), and resisted the temptation to pad the source list with unverifiable or wrongly-licensed repos.

## Mandatory disclaimer compliance

The verbatim disclaimer — **"This skill produces methodology guidance only. Outputs are not regulatory submissions. Real submissions must be authored, reviewed, and signed by qualified regulatory affairs staff and may require external counsel. No output may be filed with any regulator without sponsor authorization."** — appears in every skill body under the `## When to use` section, marked as **Mandatory disclaimer**.

## Frontmatter compliance

- `category: biotech` on all three.
- First tag is `niche:regulatory-submission` on all three.
- 4-7 additional tags on each, varied by skill focus (510k/predicate/SE for skill 2; ICH-E9/endpoints/statistical-power for skill 3; ectd/strategy/planning for skill 1).
- `license_type: free` on all three; no pricing fields populated.
- Body lengths: skill 1 ~520 lines, skill 2 ~470 lines, skill 3 ~520 lines (all within 300-700 line band).
- 5-7 URL-only sources cited per skill, mixing the verified permissive GitHub repos with regulator-public-domain URLs marked explicitly as "reference only, not a source repo."

## Confidence

**0.72.** Methodology depth is strong on the durable principles (pathway classification, substantial-equivalence reasoning, claim-vs-evidence audit) and the structural insights from the verified permissive sources. The principal confidence drag is the source thinness disclosed above — the methodology rests heavily on long-standing industry common knowledge plus regulator-public-domain references rather than on a deep corpus of permissive GitHub work. A regulatory affairs professional reading the skills will recognize the methodology as competent first-draft guidance; they should not mistake it for a substitute for current agency-specific expertise. The disclaimer in every body makes this explicit.
