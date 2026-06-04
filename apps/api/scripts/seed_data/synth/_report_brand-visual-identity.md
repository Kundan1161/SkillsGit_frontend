# Curation Report — Brand Visual Identity (Wave 7)

**Niche:** Creative — brand visual identity systems (logo systems, brand guidelines authoring, design tokens-source, asset libraries).

**Wave:** 7. Wave-4-onward methodology recovery doctrine applies: agents may read CC-BY / CC-BY-SA / proprietary brand documentation, write 100% original instructional prose informed by that reading, cite source URLs in `## Sources reviewed` with license tags, and confine trademarks to source-citation URLs only.

## Skills produced

1. `brand-system-architect.skills.md` — Design the foundational visual layer of a brand: logo and lockups, primitive and semantic color, type and scale, iconography, photography and illustration direction, motion principles, and voice cues. Includes an accessibility floor, a token-handoff layer, and a rollout plan.

2. `brand-guidelines-authoring.skills.md` — Author the brand guidelines document. Covers the four-audience model (internal designer, internal non-designer, external partner, press), canonical-format decision (site vs PDF vs both), versioning discipline with a public changelog, asset-repository conventions, and external usage terms.

3. `logo-system-construction-methodology.skills.md` — Construct the full logo system: primary and secondary marks, responsive cascade, favicon and app-icon set, clear space and minimum size, dark and light, extreme-size variants, color variants, optical correction, production file matrix (SVG / PDF-X / EPS / favicons), trademark prep checklist for counsel, and retirement plan.

4. `brand-asset-pipeline.skills.md` — Operate the asset library: source-of-truth choice (Git, DAM, Figma, hybrid), naming and folder conventions, rights metadata, derivative generation pipeline, partner distribution with audit trails, retirement of outgoing marks, and a quarterly audit cadence.

## Scope boundary against the existing token-system critic

The existing `design-token-system-critic.skills.md` audits a proposed design token system from the consumer side (a structured token tree, naming, theme-ability, dark-mode coverage, accessibility floor). The four skills above sit upstream of that audit: they design the brand visual system that feeds tokens, they author the guidelines that document the system, they construct the logos that the tokens never carry, and they operate the asset library that distributes everything the token system cannot. The `brand-system-architect` skill explicitly hands off to a token system as a downstream artifact rather than authoring tokens itself.

## Sources reviewed (with license tags)

- https://brand.github.com/ — proprietary brand-toolkit prose; read for principle extraction; trademarks not used as anchors in body.
- https://brand.github.com/foundations/logo — proprietary; read for logo-system principles.
- https://design.gitlab.com/ — CC-BY-SA 4.0 (handbook-as-code); brand-introduction and logo pages.
- https://handbook.gitlab.com/handbook/marketing/brand-and-product-marketing/design/ — CC-BY-SA 4.0; brand creative handbook.
- https://design.gitlab.com/brand-logo/logomark/ — CC-BY-SA 4.0.
- https://carbondesignsystem.com/elements/color/overview/ — Apache-2.0 system; brand prose CC-BY 4.0; color-palette and accessibility floor patterns.
- https://github.com/finos/branding — CDLA-Permissive; fintech-foundation branding pattern with program-logos and document templates.
- https://github.com/knative/community/blob/main/BRANDING.MD — CC-BY 4.0; open-source-project branding document.
- https://github.com/sturobson/brand-resources — MIT; curated collection of brand-guideline references.
- https://github.com/jcklpe/open-source-branding-toolkit — CC-BY-SA family per repo; dev-friendly starter for OSS branding.
- https://github.com/open-life-science/branding — CC-BY 4.0; community brand-asset hub.
- https://github.com/VoltAgent/awesome-design-md — MIT; collection of DESIGN.md files from public design systems.
- https://cfpb.github.io/design-system/foundation/logo — CC0 / US federal public domain; logo clear-space pattern.
- https://billsba.github.io/design-manual/brand-guidelines/logo.html — CC0 / US federal public domain; design-manual logo pattern.
- https://github.com/jonkwheeler/logo-grid — MIT; responsive-logo React component.
- https://docs.github.com/en/contributing/style-guide-and-content-model/style-guide — CC-BY 4.0 docs; voice and tone reference.
- https://github.com/18F/content-guide — CC0 / public domain; voice-and-tone patterns.
- https://www.patternfly.org/ux-writing/brand-voice-and-tone/ — MIT; voice-and-tone reference.
- https://github.com/stillwwater/UnityStyleGuide — MIT; naming-convention patterns for file-based asset libraries.

All trademarks (the GitHub Brand Toolkit, GitLab Pajamas, IBM Carbon, FINOS, Knative, Open Life Science, CFPB, SBA, PatternFly, Unity) appear only in source-citation URLs as required by wave-4 policy. No trademarked product or methodology names appear as anchors in any skill name, frontmatter, or body content.

## Methodology patterns identified across sources

- **Three-layer color token model** (primitive ramps, semantic roles, component tokens) is now the de facto pattern across Carbon, GitLab Pajamas, Microsoft Fluent, VA.gov, and CFPB. The brand-system architect skill encodes the primitive-and-role split and pushes component tokens to the token-system layer downstream.
- **Logo responsive cascade** by size bucket (favicon, symbol, symbol-plus-short-wordmark, full combination, hero) is the consistent pattern across GitHub, GitLab, CFPB, SBA, and the curated brand-resources collection. Coded as steps 7 and 8 of the logo-system skill.
- **Clear space expressed as a multiple of an internal unit** (cap height, x-height, symbol unit) rather than absolute pixels is universal. Coded as step 9 of the logo-system skill and step 6 of the brand-system architect.
- **Four-audience model for guidelines** (internal designer, internal non-designer, external partner, press) is implicit across most documented brand sites and explicit in several. Coded as step 1 of the guidelines-authoring skill.
- **Source-of-truth singularity** (one canonical, others mirror) is a pattern emphasized by every source that has scaled. Coded into all three operational skills.
- **Don't-use catalog as specific labeled negatives** rather than abstract prohibitions is the GitHub Brand Toolkit pattern, repeated in CFPB, SBA, and GitLab. Coded as step 7 of the brand-system architect and step 15 of the logo-system skill.
- **Generated derivatives, never hand-edited** is the OSS pattern from awesome-design-md, FINOS, knative, and Open Life Science. Coded as the central rule of the asset-pipeline skill.
- **Rights metadata travels with the file** is the DAM-product pattern but is implementable in repositories via sidecar files or commit-message conventions. Coded as step 7 of the asset-pipeline skill.
- **Retirement of outgoing marks is a staged, dated, notified process** is consistent across brand-refresh case studies. Coded as step 20 of the asset-pipeline skill.

## Confidence

**High confidence** in the structural skills (brand-system-architect, brand-guidelines-authoring, brand-asset-pipeline) — the patterns are well-attested across many sources and converge on consistent practice.

**Medium-high confidence** in the logo-construction skill — optical correction and trademark-prep are areas where source material is descriptive rather than prescriptive, and the methodology defers correctly to designer judgment and to qualified counsel rather than over-claiming.

**Low risk of trademark or license violation** — all trademarks confined to source URLs per policy, no source prose copied, no derivative work claims, and the asset-pipeline and trademark-prep skills explicitly defer legal and counsel work to humans with the rights.

## Notes on what was deliberately not produced

- No skill for designing the primary mark from scratch. That work belongs to a designer, not a methodology checklist; the logo-system skill explicitly says so.
- No skill for selecting a specific DAM product. The asset-pipeline skill produces a conventions and architecture document that any tool can implement.
- No skill that overlaps the existing design-token-system-critic. The brand-system-architect skill hands off to a token system as a downstream artifact and does not duplicate the audit.
- No skill that performs a trademark search. The logo-system-construction skill produces the artifact set counsel needs and clearly states that the search is counsel's work.
