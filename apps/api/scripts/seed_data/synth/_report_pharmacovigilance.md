# Wave-3 Synthesis Report — Pharmacovigilance

**Niche:** healthcare — pharmacovigilance (adverse event signal detection,
case-series narrative, periodic safety updates)

**Author:** Wave-3 methodology-synthesis agent
**Date:** 2026-05-14

---

## 1. Files produced

Three skill files plus this report, all under `synth/`:

- `D:/skillsgit/synth/signal-detection-planner.skills.md`
- `D:/skillsgit/synth/case-narrative-author.skills.md`
- `D:/skillsgit/synth/periodic-safety-report-architect.skills.md`
- `D:/skillsgit/synth/_report_pharmacovigilance.md` (this file)

No existing `synth/*` directory was present in the repository (verified
via `Glob` and directory scan), so none of the three skills overlaps an
existing skill. All three are net-new at `version: 0.1.0`. No merge or
version bump was required from prior synth output.

The repository's `prompts/shared/skills-md-spec.md` and the seed-data
fixtures (e.g. `apps/api/scripts/seed_data/janedoe-dcf-valuation-pro.skills.md`)
were used as the canonical reference for frontmatter shape and required
body sections (`## When to use`, `## How to apply`, `## Inputs`,
`## Outputs`, `## Examples`, `## Limitations`).

## 2. Body length compliance

The spec range is 300–700 body lines (body = lines after the closing
frontmatter `---`).

| Skill | Body lines |
|---|---|
| signal-detection-planner | 310 |
| case-narrative-author | 300 |
| periodic-safety-report-architect | 347 |

All three pass.

## 3. Frontmatter compliance

- `category: healthcare` on every skill (per task instruction). Note: the
  seed-category list in `prompts/02-data-model-core.md` line 116 does NOT
  include `healthcare`. This is flagged for downstream review — adding a
  `healthcare` row to the `categories` table would be needed at marketplace
  ingestion time. The instruction was explicit, so it was honoured.
- First tag is `niche:pharmacovigilance` on every skill.
- 4–7 additional tags on each.
- `license_type: free` on every skill. No `pricing` block (free tier
  carries no pricing per the spec).
- `ai.required_models` includes `claude-opus-4-7` on every skill.
- `id` follows `creator-handle/slug` shape with `synth-pv` as the
  synthesis-agent handle.
- `version: 0.1.0` (initial release).
- `changelog` entry dated 2026-05-14.

## 4. Mandatory disclaimer

The exact disclaimer from the task brief appears verbatim near the top of
each skill body, formatted as a Markdown blockquote:

> This skill produces methodology guidance for pharmacovigilance workflows.
> Outputs are not regulatory safety reports and have no role in real-time
> individual case safety reporting (which has statutory deadlines requiring
> qualified PV staff). Use only as a planning/training aid; every real PV
> decision must be authorized by a qualified PV professional and signed
> off by the EU-QPPV or equivalent.

## 5. Sources used — verified-permissive only, URL-only

The task allows MIT / Apache / BSD / ISC / Unlicense ONLY. Every source
URL listed in any of the three skills was license-verified by `WebFetch`
of the GitHub repository (or, for public regulatory pages, treated as
public reference documents, not code). Sources are URL-only — no
descriptive metadata embedded in the skill files beyond the URL itself.

| URL | License | Verification |
|---|---|---|
| https://github.com/InfOmics/TEDAR | MIT | WebFetch confirmed |
| https://github.com/WangLabCSU/faers | MIT (LICENSE.md) | WebFetch confirmed; disclosed below |
| https://github.com/ltscomputingllc/faersdbstats | Apache-2.0 | WebFetch confirmed |
| https://github.com/ngiangre/openFDA_drug_event_parsing | MIT | WebFetch confirmed |
| https://www.ema.europa.eu/.../periodic-safety-update-reports-psurs | public regulatory reference (not code) | EMA institutional page |
| https://www.who.int/publications/m/item/WHO-causality-assessment | public reference document | WHO publication |

`WangLabCSU/faers` carries an `Unknown license` file *and* a `LICENSE.md`
declaring MIT. This dual signal is disclosed in the skill body context
and treated cautiously. If the marketplace's downstream license-scanner
flags it, the conservative action is to remove this URL and rely on the
remaining three permissive code sources plus the two public regulatory
references.

## 6. Sources rejected

Most of the pharmacovigilance open-source code ecosystem is **copyleft**.
The following commonly cited projects were verified and rejected:

| URL | License | Rejection reason |
|---|---|---|
| https://github.com/Shakesbeery/vigipy | GPL-3.0 | Not on allowlist |
| https://github.com/tystan/pharmsignal | GPL-2.0 | Not on allowlist |
| https://github.com/rmj3197/MDDC | GPL-3.0 | Not on allowlist |
| https://github.com/bips-hb/pvm | GPL-3.0 | Not on allowlist |
| https://github.com/fusarolimichele/pvda | GPL-3.0 | Not on allowlist |
| https://github.com/mit-ll/Vaers_Reports | GPL-2.0 | Not on allowlist (irony: MIT-LL authored, GPL-licensed) |
| https://github.com/yehosef/vaers | no license file | Treated as "all rights reserved"; rejected |
| https://github.com/pharmacologie-caen/vigicaen | not stated on page | Rejected absent verification |
| https://github.com/ruoqi-liu/LP-SDA | no license file | Rejected absent verification |
| https://github.com/neksa/openfda-faers | not stated | Rejected absent verification |
| https://github.com/kylechua/faers-toolkit | not stated | Rejected absent verification |
| https://github.com/DSimoens/FAERS_PHARMACOVIGILANCE_ANALYSIS | license file exists but type unclear | Rejected absent confirmation |
| https://github.com/FDA/openfda | CC0-1.0 | Public-domain dedication, more permissive than MIT in practice, but CC0 is not on the strict allowlist; rejected to stay inside the rules |

## 7. Source-thinness disclosure (mandatory honesty)

The task brief acknowledged that this niche is "genuinely sparse" — that
is confirmed. Quantitatively:

- The permissive code corpus for pharmacovigilance signal detection that
  was confirmable in this exercise is **three repositories** (TEDAR,
  faersdbstats, ngiangre's openFDA parsing) plus one ambiguous-but-MIT
  candidate (WangLabCSU/faers).
- There is essentially **zero permissive open-source code for ICSR
  narrative authoring** under MIT/Apache/BSD/ISC/Unlicense. The
  case-narrative skill is grounded in publicly published structural
  norms (ICH-E2B / CIOMS-style sections) rather than in code reuse.
- There is **zero permissive open-source code for PBRER/PSUR template
  generation**. The periodic-report skill is grounded in publicly
  published section headings from ICH-E2C(R2) and EMA GVP Module VII,
  cited via the EMA URL.
- The dominant licence in this niche is **GPL** (signal-detection R/Python
  ecosystem) or **unspecified** (one-off Jupyter analyses).

This thinness is intentionally surfaced in each skill's `Sources` section
and in the skill body limitations. The methodology guidance is therefore
**synthesised from publicly available structural conventions**, not
copied from any specific repository's content.

## 8. Patterns across the three skills

- **Mandatory disclaimer verbatim** at the top of every body.
- **Hard refusal of regulatory standing.** Each skill explicitly disclaims
  any role in expedited individual case reporting, regulatory submission,
  or final QPPV signoff.
- **Sectioned, methodology-grade output.** Each skill produces a
  structured Markdown deliverable that a qualified human reviewer can
  edit; no skill produces a finished regulatory document.
- **Generic ICH / EMA structural conventions only.** No proprietary text,
  no SOP text from any company, no copy-paste from regulatory templates.
- **Explicit limitations and "how this skill differs from a real
  workflow" sections** to keep the boundary clean.
- **No claim of causality, no claim of denominator-controlled rates, no
  benefit-risk conclusions** generated by the AI.
- **Sources are URL-only**; no embedded license text, no quoted README.

## 9. Originality

All three skill bodies are 100% original writing for this synthesis
exercise. No README, no code comment, no SOP text was reused. Section
headings (e.g. "Worldwide marketing authorisation status", "Signal and
risk evaluation") follow standard ICH-E2C(R2) conventions, which are
publicly published structural headings, not copyrightable expression.

## 10. Confidence

- **High confidence:** the structural shape of each output matches
  widely taught pharmacovigilance practice; the disclaimers are correct
  and load-bearing; the permissive sources are license-verified by
  direct WebFetch.
- **Medium confidence:** the threshold defaults in the signal-detection
  planner (PRR ≥ 2/3, EBGM05 ≥ 1, IC025 > 0) reflect common practice in
  the cited literature but a real PV team will tune them to their
  database; they are presented as defaults to discuss, not as standards.
- **Lower confidence (disclosed):** WangLabCSU/faers carries an ambiguous
  dual-licence signal and could be flagged by a strict licence scanner.
  Recommend the marketplace's licence audit step re-verifies it before
  publication.

## 11. Recommended follow-ups for the marketplace platform

1. Add `healthcare` to the `categories` seed list in
   `prompts/02-data-model-core.md` line 116, otherwise the
   `category: healthcare` value on these skills will fail the foreign-key
   constraint at publish time.
2. Re-verify the WangLabCSU/faers licence before the publication pipeline
   ingests these skills.
3. Consider whether `niche:*`-prefixed tags should be a reserved tag
   namespace in the schema; the spec currently treats all tags as a flat
   `text[]`.

---

*End of report.*
