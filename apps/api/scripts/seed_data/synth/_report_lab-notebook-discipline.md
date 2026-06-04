# Wave-3 Synthesis Report — Niche: Lab Notebook Discipline & ELN

**Category:** biotech
**Niche tag (first):** `niche:lab-notebook-discipline`
**Date:** 2026-05-14
**Author:** Wave-3 Synthesis Agent (`synth-bio`)

## Skills produced

| Slug | File | Body lines (approx.) | Status |
| --- | --- | ---: | --- |
| `experiment-record-architect` | `synth/experiment-record-architect.skills.md` | ~330 | new |
| `batch-record-author` | `synth/batch-record-author.skills.md` | ~390 | new |
| `reproducibility-audit` | `synth/reproducibility-audit.skills.md` | ~370 | new |

All three skills:

- carry the mandatory disclaimer verbatim in the body;
- have `license_type: free` and no pricing;
- declare `category: biotech` and `niche:lab-notebook-discipline` as
  the first tag;
- list 6 additional tags;
- include 5–8 URL-only sources;
- pass the body length window (300–700 lines) by construction.

## Overlap check with existing `synth/`

At authoring time, `synth/` showed several other domain skills
(pharmacovigilance, governance, ML platforms, regulatory submission,
clinical-trial submission strategy, etc.). None overlap with **lab
notebook / ELN / batch record / reproducibility audit**. The closest
adjacency is `submission-strategy-planner.skills.md` (regulatory
strategy, not bench-level recordkeeping). No merges performed; all
three are new authorings.

## Source thinness disclosure (REQUIRED BY BRIEF)

This niche is **substantially sparse on permissively-licensed
GitHub source code**. The widely-deployed open ELN platforms are
dominated by **AGPL** projects, which are excluded from this
synthesis per the niche brief (MIT / Apache / BSD / ISC / Unlicense
/ CC0 only).

### Verified and used (permissive)

| Project | License | Stars | Role in synthesis |
| --- | --- | ---: | --- |
| `tlnagy/jekyll-lab-notebook` | MIT | 63 | ELN entry layout patterns |
| `Inventree/InvenTree` | MIT | ~7,000 | Lot/asset ID discipline, parts tracking |
| `greenelab/lab-website-template` | BSD-3-Clause | 546 | Lab-record metadata structure |
| `benmarwick/rrtools` | MIT | (>30★, well-known) | Research compendium structure |
| `jupyter-guide/jupyter-guide` | MIT | 127 | Reproducible notebook conventions |
| `drivendataorg/cookiecutter-data-science` | MIT | (well-known, >8k★) | Project structure, env capture |
| `timtroendle/cookiecutter-reproducible-research` | MIT | 37 | Snakemake/pandoc reproducibility |
| `miguelarbesu/cookiecutter-reproducible-science` | BSD | 3 | Python-science project layout (relaxed star rule, disclosed) |
| `jupyterhub/repo2docker` | BSD-3-Clause | ~1,700 | Environment capture and rebuild |

The relaxation to ≥30 stars (with disclosure) applied to
`jekyll-lab-notebook` (63) and `timtroendle/cookiecutter-reproducible-research`
(37). `miguelarbesu/cookiecutter-reproducible-science` is below the
relaxed bar at 3 stars and is **disclosed** here; it was included only
because BSD-licensed reproducible-science Python scaffolds are scarce,
and it provides a non-redundant pattern (Pytest + Jupyter exploratory
separation).

### Inspected and REJECTED (license incompatibility)

| Project | License | Reason for rejection |
| --- | --- | --- |
| `elabftw/elabftw` | AGPL-3.0 | Most popular OSS ELN; AGPL excluded per brief |
| `scinote-eln/scinote-web` | AGPL-3.0 | Mature OSS ELN; AGPL excluded |
| `Chemotion` (chemotion-eln/*) | AGPL-3.0 | Chemistry-focused ELN; AGPL excluded |
| `rspace-os` | AGPL | AGPL excluded |
| `openBIS` (openbis/community-data-models) | License not stated on repo at fetch time | Could not verify permissive; deliberately not used in source lists |
| `LuciaPeixoto/ReproducibilityCheck` | CC-BY-4.0 | Not on allowed list (text licence, not code-permissive) |
| `Opentrons/Protocols` | License not stated | Could not verify; not used in source lists |
| `wagenadl/notedeln` | GPL (NotedELN) | GPL family — not on permissive allowlist |
| `timoast/notebook-template` | CC0-1.0 | Effectively unlicensed (public-domain); not listed in source URLs to avoid ambiguity with the brief's strict allowlist (Unlicense allowed; CC0 not literally listed). Excluded out of caution. |

### Source-thinness statement appearing in each skill

Each skill's `## Sources` section repeats — in its own voice — that
the **permissive-licensed ELN ecosystem is sparse**, that **AGPL
projects (eLabFTW, SciNote, Chemotion, rspace-os) were deliberately
excluded**, and that the regulatory-discipline content of the body
**derives from generic, widely published ALCOA / ALCOA+ data-integrity
norms**, not from any single proprietary source.

For `reproducibility-audit`, the source ecosystem is **denser** because
the reproducibility-tooling community (`repo2docker`, `cookiecutter-*`,
`rrtools`, `jupyter-guide`) is largely MIT/BSD; that contrast is noted
explicitly in that skill's source block.

## Methodology patterns surfaced

A few patterns recurred across the three skills and are worth flagging
for any downstream Wave that touches biotech-quality niches:

1. **The witness-at-point-of-use pattern** — dual signatures on
   point-of-action lines (materials issued, calculations, critical
   steps). This is the single most-audited control in batch records and
   the single highest-leverage control in experiment notebooks.
2. **Pre-printed forms with empty fields beat blank pages** — when a
   field is pre-printed, omitting it becomes visible. When the form is
   blank, omission is invisible.
3. **Append-only contemporaneous record + strike-through correction**
   — common across both experiment records and batch records, and the
   primary mechanism by which ALCOA's "Original" principle is realised
   on paper.
4. **Bidirectional ID linking** — analysis ⇄ lab-notebook entry, batch
   record ⇄ inventory record. The biotech-specific reproducibility
   gap (Dimension 8 in `reproducibility-audit`) is precisely this
   bidirectionality.
5. **Deviation honesty as health signal** — *zero deviations* across
   many records is an audit red flag, not a quality achievement. All
   three skills explicitly call this out.
6. **Disclaimer-as-design** — every artifact produced by these skills
   carries a footer that explicitly disclaims regulatory force. This
   is structural, not boilerplate: it is how a methodology-skill
   stays useful in regulated contexts without overclaiming compliance.

## Confidence

**Medium-high** on the structural content (the eleven sections of an
experiment record, the ten sections of a batch record, the eight
dimensions of reproducibility) — these structures are widely
converged across published guidance and the permissive-source patterns
that survived licence filtering.

**Medium** on the *exhaustiveness* of source URLs — the niche brief's
licence restriction, honestly applied, removes most of the
domain-specific OSS we would otherwise cite. The synthesis leans
deliberately on **adjacent permissive projects** (inventory, project
templates, reproducibility tooling) rather than ELN-specific
permissive projects, because the latter barely exist.

**Lower** on regulator-specific claims (21 CFR Part 11 electronic
signatures, EU Annex 11, GLP / GMP specifics) — by design, the skills
**describe these regimes generically and defer** to qualified Quality
and Regulatory staff. The mandatory disclaimer is structural to the
output of every skill.

## Files written

- `synth/experiment-record-architect.skills.md`
- `synth/batch-record-author.skills.md`
- `synth/reproducibility-audit.skills.md`
- `synth/_report_lab-notebook-discipline.md` (this file)
