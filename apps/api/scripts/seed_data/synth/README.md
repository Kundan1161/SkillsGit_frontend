# Synthesized Skills — Curation Notes

This folder contains skills.md files **authored from scratch** by area-specialist agents that surveyed public GitHub repositories in a given expertise area, identified common methodology patterns across those sources, and synthesized an original instructional document describing the methodology.

## What these files are
- Original instructional prose targeted at AI agents executing the methodology.
- Frontmatter conforming to `prompts/shared/skills-md-spec.md`.
- A `## Sources reviewed` section at the end of each skill listing the source repository URLs that informed the synthesis, each tagged with its license, with NO copied content.

## What these files are NOT
- They are not derivative works of any specific repo's code or documentation.
- They do not paste, paraphrase, or reproduce substantial portions of any source.
- They do not claim affiliation with any cited project or author.

## Source license policy

Curation evolved over several waves:

- **Waves 1–3** used a strict allowlist: **MIT, Apache-2.0, BSD-2/3-Clause, ISC, Unlicense only**. Copyleft (GPL/AGPL/LGPL/MPL), share-alike (CC-BY-SA), non-commercial (CC-BY-NC-*), and source-available (BSL/Elastic/Fair-Source) sources were rejected outright, even when they were the canonical references in the field.
- **Wave 4 onward** the policy was widened with the "methodology recovery" doctrine: source-license restrictions govern redistribution of *source code and source prose*, not knowledge *derived from reading them*. Agents may now read GPL / AGPL / CC-BY-SA / Elastic / BSL sources, write 100% original instructional prose informed by that learning, and cite the source URL in `## Sources reviewed` with an explicit `(license)` tag for buyer transparency. Trademarked product names from those sources MUST NOT appear in skill names or body content — only as repo paths in source-citation URLs.

Discipline that applies to **every** wave:

- No code is copied from any source, ever.
- No source prose is copied or close-paraphrased — agents read for understanding, not for transcription.
- Trademarked product/methodology names are confined to `## Sources reviewed` URL citations. Skill names and body content describe the underlying technique generically.
- High-stakes niches (medical, biotech, robotics, legal, regulatory) carry mandatory "qualified-staff review required" disclaimers verbatim in every body.

## Pricing

All curated skills publish at `license_type: free`. The `publish_curated.py` script in `apps/api/scripts/` forces every skill to `PricingModel.FREE` regardless of frontmatter values, while we focus on growing the library before re-introducing paid tiers. Pricing fields may appear in YAML frontmatter for historical reasons but are ignored at publish time.

## Publishing flow

1. Agents drop drafts here, named `<slug>.skills.md`.
2. The integration step validates each against `apps/api/src/skills/validator.py`. Failures are reported with field-level error codes.
3. Valid skills publish under the platform creator account `@skillsgit-curated` via `apps/api/scripts/publish_curated.py`. The script is idempotent on `(creator_handle, slug)` — re-running updates mutable listing metadata and only creates new `SkillVersion` rows when the frontmatter version changes.
4. All publishes land directly in `published` status (no manual moderation queue) since these are platform-curated. The standard `pending_review → published` flow is reserved for third-party creators.

## Synthesis reports

Each curation wave also produces `_report_<niche>.md` files documenting sources reviewed (with license tags), rejection reasoning, methodology patterns identified, and confidence levels. These reports are the audit trail for the library's curation discipline.
