# Wave-4 Methodology Synthesis — Open Financial Analytics & Quant Tooling Methodology

**Niche:** `finance / niche:open-financial-analytics`
**Date:** 2026-05-14
**Agent run:** Wave-4 methodology-recovery
**Policy posture:** Strict — AGPL repos READ for methodology and CITED with `(AGPL-3)` tag only. No code reuse, no prose copying, no close paraphrase. No trademarked names used as methodology anchors in body content.

## Files produced

1. `synth/finance-equity-research-workflow-designer.skills.md` — designs a repeatable equity-research workflow with hypothesis, fundamental/technical layers, peer comp, scenarios, risks, recommendation memo.
2. `synth/finance-factor-research-pipeline-architect.skills.md` — designs a factor-research pipeline with point-in-time correctness, look-ahead avoidance, multi-period backtest, robustness, decay.
3. `synth/finance-alternative-data-evaluation-framework.skills.md` — seven-dimension evaluation of an alt-data source: coverage, latency, accuracy, signal/noise, decay, capacity, vendor risk, ROI.
4. `synth/finance-research-memo-author.skills.md` — short-form investment research memo authoring discipline: claim, evidence, mechanism, falsifiers, sizing, exit triggers.

Four skills delivered. No prior skills covering open-financial-analytics niche existed in `synth/` (verified — prior finance skills covered FP&A and accounting, no overlap).

## Sources reviewed (with licenses)

All sources verified for license. AGPL repos cited with explicit `(AGPL-3)` tag and noted as methodology-only reference; no code or prose was copied or paraphrased.

### Repositories cited across the four skills

- **https://github.com/microsoft/qlib** — **MIT**. Quant investment platform; informed data-layer, factor-construction, backtest, and decay diagnostics methodology.
- **https://github.com/quantopian/alphalens** — **Apache-2.0**. Factor analysis library; informed information-coefficient, quantile-spread, turnover, and decay diagnostics.
- **https://github.com/JerBouma/FinanceToolkit** — **MIT**. Fundamental analysis and ratios; informed equity-research fundamental-layer methodology.
- **https://github.com/ranaroussi/yfinance** — **Apache-2.0**. Equity data access; informed data-ingestion considerations.
- **https://github.com/AI4Finance-Foundation/FinRobot** — **Apache-2.0**. AI agent platform for financial analysis; informed workflow-stage structure across multiple skills.
- **https://github.com/pmorissette/ffn** — **MIT**. Financial functions for Python; informed performance and risk-diagnostic methodology in factor pipeline.
- **https://github.com/jerryxyx/AlphaTrading** — **no LICENSE file**. Cited as a *methodology pointer only* (factor pretest, combination, risk-decomposition pattern). Flagged for license verification at publish-time; if unverifiable, drop from source lists with no methodology impact.
- **https://github.com/OpenBB-finance/OpenBB** — **AGPL-3**. Cited as `(AGPL-3)` per policy. Used as a reference for the architecture of *open financial data terminals* generically; no code, no prose, no name used as a methodology anchor in any skill body. Methodology contribution: confirmed the multi-surface pattern (data layer → research surface → AI-agent interface) that underlies modern open-financial-analytics stacks.

### Coverage per skill

- **equity-research-workflow-designer:** qlib (MIT), FinanceToolkit (MIT), yfinance (Apache-2.0), FinRobot (Apache-2.0), AlphaTrading (methodology pointer), alphalens (Apache-2.0), OpenBB (AGPL-3 reference).
- **factor-research-pipeline-architect:** qlib (MIT), alphalens (Apache-2.0), AlphaTrading (methodology pointer), FinanceToolkit (MIT), ffn (MIT), yfinance (Apache-2.0), FinRobot (Apache-2.0), OpenBB (AGPL-3 reference).
- **alternative-data-evaluation-framework:** qlib (MIT), alphalens (Apache-2.0), FinanceToolkit (MIT), yfinance (Apache-2.0), FinRobot (Apache-2.0), AlphaTrading (methodology pointer), OpenBB (AGPL-3 reference).
- **research-memo-author:** qlib (MIT), FinanceToolkit (MIT), yfinance (Apache-2.0), FinRobot (Apache-2.0), alphalens (Apache-2.0), AlphaTrading (methodology pointer), OpenBB (AGPL-3 reference).

## Patterns observed across the niche

1. **The pipeline shape is universal.** Across permissively-licensed and AGPL repos alike, the same coarse pipeline recurs: universe definition → data ingestion → feature/factor construction → portfolio formation → backtest → diagnostics. The skills synthesize this generic shape; no specific implementation is reproduced.
2. **Point-in-time discipline is the single highest-leverage technical detail.** The factor-pipeline literature (academic and open-source) agrees this is where most pipelines silently leak. The factor-research skill leans hard into it (Stage 3 is dedicated to it; the universe-definition stage requires it; the backtest design tests it).
3. **Diagnostics matter more than headlines.** Strong factor work emphasizes IC information ratio, decay profile, robustness halo, capacity, and cost overlay — not just headline Sharpe. The factor and alt-data skills both encode this.
4. **Alternative data evaluation has no canonical open-source library**, but the seven-dimension structure (coverage, latency, accuracy, signal/noise, decay, capacity, vendor risk, ROI) recurs across vendor RFPs, industry blogs, and adjacent academic literature.
5. **The research memo is the connective tissue between research and decision.** Workflow and factor pipeline produce evidence; the memo turns evidence into a falsifiable, sized, pre-committed position. The fourth skill is built around this discipline.
6. **AGPL gravity is real in this niche.** The most-discussed open-source financial data terminal is AGPL, which prevents code reuse. Methodology can be learned from it but the skills cite it only by URL and explicit license tag, with no name in the methodology body.

## Methodology-vs-expression boundary checks

- **No name of any trademarked tool or AGPL project appears in any skill's body** as a methodology anchor. AGPL projects are referenced only in the `## Sources reviewed` section with an explicit `(AGPL-3)` tag and the note "referenced for methodology of open financial data terminals; no code or prose reused."
- **Generic technique names used throughout**: "open-data financial terminal", "factor-research pipeline", "alt-data evaluation framework", "information coefficient", "quantile spread", "point-in-time data protocol", "robustness halo". These are field-standard generic terms, not trademarked.
- **No code, README prose, doc prose, or close paraphrase from any source repo appears in any skill.** All methodology synthesis is in 100% original prose written for this task.
- **No copied tables, no copied diagrams, no copied parameter values.** Example numbers in worked examples are generic placeholders or stylized illustrative values, not drawn from any specific repo.
- **License-free methodology only.** The patterns synthesized — pipeline stages, point-in-time protocols, IC/quantile diagnostics, robustness testing, decay monitoring, alt-data evaluation dimensions, memo structure with falsifiers and exit triggers — are field-standard practice that exists in the literature, academic papers, vendor blogs, and across many open-source projects. Synthesis here describes the practice generically; it does not derive from any single source.

## Rejections / cautions

- **OpenBB-finance/OpenBB** — AGPL-3. Per policy, READ for methodology and CITED with explicit `(AGPL-3)` tag. The project name is NOT used in any skill body as a methodology anchor; methodology is described generically as "open-data financial terminal" or "open financial data integration layer."
- **jerryxyx/AlphaTrading** — No LICENSE file detected during research. Included only as a methodology pointer in source lists with explicit flagging. If license verification at publish-time fails, drop from all four skills' source lists; no methodology depends on it.
- **Some highly relevant adjacent repos (Zipline, Pyfolio, bt, Pyfolio-Reloaded)** were not separately fetched in this run; they are well-known in this niche but the methodology contributions overlap heavily with alphalens, qlib, and ffn which were verified. If the platform later wants deeper sourcing on backtesting frameworks specifically, these would be the next candidates (typically Apache-2.0 or similar permissive).

## Source-thinness disclosure

The niche has solid permissively-licensed sources for the *factor research* and *equity research data infrastructure* sides (qlib, alphalens, FinanceToolkit, ffn, yfinance). It is genuinely thin on the *workflow design*, *memo authoring discipline*, and *alt-data evaluation* sides, because much of that knowledge lives in proprietary playbooks, paid consulting deliverables, and the AGPL-licensed terminal that this skill set cannot lean on for code or prose. The skills are honest about this — they cite the available permissive repos as methodology touch-points and synthesize the broader practice that those repos sit inside.

The most prominent open-source product in this niche (OpenBB) is AGPL-licensed. Per policy, it is referenced as a methodology pointer with the explicit license tag, and the project name is not used in any skill body. If OpenBB ever relicenses under MIT/Apache, all four skills would benefit from re-citing without the methodology-anchor restriction.

## Confidence

- **High confidence** on methodology content for all four skills. The patterns (pipeline stages, point-in-time protocols, IC/quantile diagnostics, decay analysis, alt-data evaluation dimensions, memo structure with falsifiers and pre-committed exits) are well-established field practice and the synthesis is faithful.
- **High confidence** on policy compliance: AGPL repos are read-only and cited with explicit `(AGPL-3)` tags; trademarked product names do not appear as methodology anchors in any skill body; all prose is 100% original; no close paraphrase or code reuse.
- **High confidence** on frontmatter conformance: `license_type: free`, no pricing, `category: finance`, first tag `niche:open-financial-analytics`, 6-7 subsequent tags, `skillsgit-curated/{slug}` ID format.
- **High confidence** on body-length compliance: each file is between 307 and 326 lines, within the 300-600 target. All required sections (`## When to use`, `## How to apply`, `## Inputs`, `## Outputs`, `## Examples`, `## Limitations`, `## Sources reviewed`) present.
- **High confidence** that every skill includes the "outputs are not investment advice" disclaimer in the `## When to use` and `## Limitations` sections, framed appropriately for the audience.
- **Medium confidence** on `jerryxyx/AlphaTrading` license cleanliness; flagged for publish-time verification. Removal would not affect methodology depth as it is cited only as a pointer alongside several verified sources.

## Follow-ups recommended

1. **License verification pass at publish-time.** Validator should re-verify `jerryxyx/AlphaTrading` license; if no LICENSE file is confirmable, drop from source lists. No methodology impact.
2. **AGPL citation policy review.** The four skills cite OpenBB once each with explicit `(AGPL-3)` tags as a methodology pointer. If the platform prefers no AGPL citations at all, the citations can be removed without methodology change — they are pointers, not foundations.
3. **Watch for niche-deepening opportunities.** If a major MIT/Apache-licensed open financial terminal emerges, the skills' methodology pointers should be updated. Worth a quarterly review.
4. **Consider commissioning worked-example datasets.** As with the FP&A wave, the open data in this niche is thin on rich worked examples that meet license cleanliness. Synthetic but realistic example datasets (a factor panel, an alt-data sample, a research memo case) would strengthen the examples in each skill.
5. **Validator regression.** Each skill should pass `apps/api/src/skills/validator.py` before publish. Frontmatter follows the established `synth/` pattern (e.g., `finance-scenario-model-builder.skills.md` was used as the reference structure).
6. **Cross-skill consistency.** The four skills share definitional posture on point-in-time, IC, quantile spread, decay, falsifiers, and exit triggers. If the platform later writes a finance glossary skill, ensure definitions across these four remain pinned.

---

End of report.
