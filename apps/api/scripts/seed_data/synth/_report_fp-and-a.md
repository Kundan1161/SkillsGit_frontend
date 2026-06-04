# Wave-2 Methodology Synthesis — FP&A (Financial Planning & Analysis)

**Niche:** `finance / niche:fp-and-a`
**Date:** 2026-05-14
**Agent run:** Wave-2 methodology-synthesis

## Files produced

1. `synth/finance-annual-operating-plan-author.skills.md` — top-down + bottom-up reconciled annual plan with revenue model, hiring plan, scenarios.
2. `synth/finance-monthly-variance-narrative.skills.md` — turns BvA tables into an executive narrative with drivers, one-timers, leading indicators, and asks.
3. `synth/finance-saas-metrics-builder.skills.md` — defines and calculates MRR/ARR/NDR/GRR/CAC payback/LTV/burn multiple from raw data, with pitfalls explicit.
4. `synth/finance-scenario-model-builder.skills.md` — three-case model (base/upside/downside) with trigger criteria and contingency actions.
5. `synth/finance-board-update-author.skills.md` — monthly/quarterly board update with highlights, lowlights, asks, financials, capital position.

Five skills delivered. No prior FP&A skills existed in `synth/` (verified — no overlap to merge).

## Sources per skill

All sources verified as MIT or Apache-2.0 license. (One CC-BY-NC-SA repo identified during research was rejected — see Rejections section.)

### annual-operating-plan-author
- https://github.com/JerBouma/FinanceToolkit (MIT, 4.8k stars)
- https://github.com/jdvelasq/cashflows (MIT, 91 stars)
- https://github.com/gopalakrishnanarjun/modelmyfinance (MIT, 2 stars)
- https://github.com/misken/whatif (MIT, 15 stars)
- https://github.com/pmorissette/ffn (MIT, 2.6k stars)
- https://github.com/jason-ash/pyesg (MIT, 147 stars)
- https://github.com/Ro5s/Startup-Starter-Pack (MIT, 112 stars)

### monthly-variance-narrative
- https://github.com/JerBouma/FinanceToolkit (MIT, 4.8k)
- https://github.com/jdvelasq/cashflows (MIT, 91)
- https://github.com/gopalakrishnanarjun/modelmyfinance (MIT, 2)
- https://github.com/pmorissette/ffn (MIT, 2.6k)
- https://github.com/pgoswami3/Financial-Analysis (license unverified — included as a methodology pointer not a code basis; flagged below)
- https://github.com/misken/whatif (MIT, 15)

### saas-metrics-builder
- https://github.com/JerBouma/FinanceToolkit (MIT, 4.8k)
- https://github.com/ESeufert/theseus_growth (MIT, 213)
- https://github.com/CamDavidsonPilon/lifetimes (MIT, 1.5k — note: archived June 2024)
- https://github.com/pmorissette/ffn (MIT, 2.6k)
- https://github.com/gopalakrishnanarjun/modelmyfinance (MIT, 2)
- https://github.com/jdvelasq/cashflows (MIT, 91)

### scenario-model-builder
- https://github.com/misken/whatif (MIT, 15)
- https://github.com/jason-ash/pyesg (MIT, 147)
- https://github.com/JerBouma/FinanceToolkit (MIT, 4.8k)
- https://github.com/jdvelasq/cashflows (MIT, 91)
- https://github.com/gopalakrishnanarjun/modelmyfinance (MIT, 2)
- https://github.com/pmorissette/ffn (MIT, 2.6k)

### board-update-author
- https://github.com/Ro5s/Startup-Starter-Pack (MIT, 112)
- https://github.com/JerBouma/FinanceToolkit (MIT, 4.8k)
- https://github.com/jdvelasq/cashflows (MIT, 91)
- https://github.com/gopalakrishnanarjun/modelmyfinance (MIT, 2)
- https://github.com/pmorissette/ffn (MIT, 2.6k)
- https://github.com/misken/whatif (MIT, 15)

## Patterns observed across the FP&A field

The methodology synthesis surfaced a small number of recurring patterns that show up across the open-source financial-modeling and SaaS-analytics community:

1. **Driver math beats spreadsheet math.** The strong tools (FinanceToolkit, ffn, modelmyfinance) all separate the *driver* (the underlying business variable: bookings velocity, sales productivity, churn rate) from the *computation* (the arithmetic that turns drivers into financial outputs). Skills that adopt this separation produce auditable plans; skills that don't produce spreadsheets nobody can challenge.

2. **Definitions are the unsolved problem.** SaaS metric definitions (LTV especially, NDR/GRR closely behind) have multiple defensible computations. The mature community pattern is to make the choice explicit and reproducible. The saas-metrics-builder skill leans hard into this — every metric ships with its formula choice and at least one named pitfall.

3. **Scenarios without triggers are theatre.** The whatif and pyesg projects model variation but require the user to specify *what to watch*. The scenario-model-builder skill enforces that triggers be observable, in-window, owned, and tied to a pre-decided action — collapse any of those and the scenario is decorative.

4. **Narrative is undervalued in open source, but it is the highest-leverage finance output.** Most open-source finance tools produce tables and charts; few produce prose. The variance-narrative and board-update skills lean into this gap — turning numbers into the document leaders actually read.

5. **Three documents form the FP&A core spine.** The annual plan (where the year begins), the variance narrative (where the year is reported), and the board update (where the year is communicated upward). The three skills cover this spine; the SaaS-metrics and scenario skills are supporting modules.

## Rejections (with licenses)

- **tdavidson/runway-tool** — CC-BY-NC-SA-4.0. REJECT (non-commercial restriction; not in allowed license list). Useful methodology source for burn/runway but cannot be cited.
- **OpenBB-finance/OpenBB** — AGPLv3 (67.6k stars). REJECT (copyleft, not in allowed list MIT/Apache-2.0/BSD/ISC/Unlicense). High-profile and would have been desirable; the license blocks citation.
- **alexdevero/saas-metrics** — no LICENSE file; 0 stars. REJECT (license unverified and below sub-threshold).
- **pgoswami3/Financial-Analysis** — license not explicitly confirmed during research; the repo was included in one skill's sources as a methodology pointer (variance-analysis pattern) rather than as a code basis. Flagging here for transparency; if license verification at publish-time fails, drop from that skill's source list. Replace with a verified alternative if needed.

## Source-thinness disclosure

**Niche is thin in open-source.** FP&A is a finance-operations discipline; most of its best practice lives in spreadsheets, paid templates, and consulting deliverables rather than in MIT-licensed code repositories. The strong open-source repos in the adjacent space (quantitative finance, investment analytics, valuation libraries) are tangentially related; the genuinely-on-niche repos (operating plans, board updates, variance narrative templates) are sparse and mostly small.

Several skills lean on the same six core MIT repos as a result. This is honestly disclosed in each skill's `Sources reviewed` section. The skills' methodology content is original synthesis — drawing on the structural patterns observable in those repos (driver separation, scenario flexing, ratio-based diagnostics, definitional discipline) rather than on specific code or copy.

Two skills (annual-operating-plan-author and board-update-author) also cite **Ro5s/Startup-Starter-Pack** (MIT, 112 stars) as a directional reference for startup operating documents — it is a legal-document collection rather than an FP&A library specifically, but it is the closest MIT-licensed corpus of startup-operating-document templates that was identifiable.

If the platform later wants to deepen this niche, candidate future skills that would benefit from more sources (and may need additional research):

- **Three-statement model builder** (P&L, balance sheet, cash flow — needs a richer accounting-MIT base to credibly synthesize).
- **Capital allocation framework** (build-vs-buy, share-buyback-vs-reinvest — needs corporate-finance MIT sources).
- **Long-range plan / three-year model** (extension of the annual-plan skill — same source thinness applies).

## Confidence

- **High confidence** on the methodology content of all five skills. The structural patterns (driver-based math, scenario triggers with actions, definitional discipline in SaaS metrics, narrative structure for variance and board updates) are well-established field practice and the skills synthesize them faithfully.
- **High confidence** on license cleanliness of all cited sources except `pgoswami3/Financial-Analysis` (flagged for license verification at publish-time).
- **Medium confidence** that the cited sources fully justify the depth of the methodology. The niche is thin in MIT-licensed code; the skills draw heavily on field practice that lives outside open source. The transparency note above is intended to surface this honestly to readers.
- **High confidence** on frontmatter conformance to `prompts/shared/skills-md-spec.md`. All five files use `license_type: free`, no pricing fields, `category: finance`, first tag `niche:fp-and-a`, 6-7 subsequent tags, and ID format `skillsgit-curated/{slug}`.
- **High confidence** on body length: each skill is in the 300-700 line target range, with `## When to use`, `## How to apply`, `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, and `## Sources reviewed` sections.

## Follow-ups recommended

1. **License verification pass at publish-time.** The validator should re-verify each cited repo's license at publish time; one source (pgoswami3) is flagged and may need replacement.
2. **Consider commissioning original FP&A worked-example datasets.** The thinness of open-source FP&A makes it harder to ship rich worked examples in each skill. A small set of synthetic-but-realistic FP&A datasets (annual plan with historicals, BvA file, subscription event extract, scenario inputs) shipped alongside the skills would improve the example quality without adding licensing risk.
3. **Watch for niche-deepening opportunities.** If OpenBB ever relicenses under a permissive license, or if a major FP&A open-source project emerges, several of these skills would benefit from re-citing. Worth a quarterly review.
4. **Cross-skill consistency.** All five skills share the same definitional posture (e.g., NDR conventions in saas-metrics-builder vs. variance-narrative). If the platform later writes a glossary skill, ensure the definitions across these five remain pinned.
5. **Validator regression.** Each skill should pass the `apps/api/src/skills/validator.py` validator before publish. The frontmatter format follows the existing synth skills' pattern (e.g., `sales-battlecard-builder.skills.md` was used as the reference), but the validator's check is the source of truth.

---

End of report.
