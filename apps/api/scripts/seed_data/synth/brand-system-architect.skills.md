---
id: skillsgit-curated/brand-system-architect
version: 1.0.0
name: Brand Visual System Architect
description: Design a complete brand visual identity system — logo plus lockups, color with semantic roles and accessibility floor, type and scale, iconography, photography and illustration direction, motion principles, and voice cues.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [brand-visual-identity, brand-system, logo-system, color-palette, typography, iconography, voice-and-tone]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - brand system
  - visual identity
  - brand identity system
  - logo system
  - brand palette
  - brand typography
  - iconography system
  - brand motion
  - brand voice
  - brand foundations
  - identity architecture
  - brand architecture
example_invocations:
  - "Design a visual identity system for our seed-stage developer-tools brand."
  - "Architect a brand system that covers logo, color, type, icons, photography, motion, and voice."
  - "Propose a brand visual system that will hold up across a marketing site, a product UI, conference signage, and partner co-branding."
  - "Define the foundational layer of our brand — palette roles, type ramp, icon family, motion principles."
inputs:
  - name: brand_brief
    type: text
    required: true
    description: A description of the brand — audience, category, competitive set, personality words, must-haves, must-avoids, existing assets if any.
  - name: surfaces
    type: text
    required: false
    description: The surfaces the system must serve — for example "marketing site, product UI, mobile app, social, print collateral, event signage, partner co-brand."
  - name: constraints
    type: text
    required: false
    description: Hard constraints — accessibility floor (WCAG level), trademark exclusions, locked typeface licenses, mandatory legal copy, parent-brand rules.
  - name: maturity_target
    type: choice
    required: false
    description: How complete the output system should be.
    choices: [foundations-only, full-system, full-system-with-extensions]
outputs:
  - name: brand_system
    type: markdown
    description: A structured brand visual system covering logo, color, type, iconography, imagery, motion, and voice, with semantic roles and an accessibility floor.
  - name: open_questions
    type: markdown
    description: Decisions left open for the brand owner, with options and recommended defaults.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Reach for this skill when an agent is asked to design the foundational visual layer of a brand or to extend an existing one into a fuller system. Typical situations:

- A founder or product team has a wordmark and a hex code and wants a system that can carry the brand across product, marketing, and partner contexts.
- An in-house team is preparing for a rebrand and needs a system blueprint before commissioning detailed design work.
- A scale-up has grown past its starter brand and needs an identity that can theme cleanly, support sub-brands, meet accessibility floors, and feed a design-token pipeline.
- A new product line needs a brand layer that nests under a parent brand without diluting it.

Skip this skill when the request is for a single artifact (one poster, one ad), when the task is a token-level audit of an existing system (see a token-system critic skill instead), or when the request is for visual taste-grading rather than system architecture. This skill produces a plan and a structured specification, not finished art.

## How to apply

Work through the layers in this order. Each layer feeds the next, and skipping a layer almost always produces incoherence further down.

1. Restate the brief.
   Capture audience, category, competitive set, personality words, and any locked constraints.
   Resist immediately picking colors or typefaces.
   Get the brief tight first.
   If the brief is silent on a critical input — accessibility floor, parent-brand rules, locked typeface licenses — surface that gap before continuing rather than assuming a default.

2. Choose three to five personality words.
   They become the rubric every later choice is measured against.
   Words like "precise, warm, plain-spoken, kinetic" steer typography, color, motion, and voice as a single decision.
   Avoid generic words ("modern, clean, bold") that do not constrain anything.
   Where two words tension against each other ("warm" and "precise"), state the resolution rule: which one wins where they cannot both be true.

3. Define the brand idea in one sentence.
   The idea is what the brand stands for in the world, distinct from what it sells.
   A strong idea constrains the system; a weak idea produces a mood board.
   Test the idea by writing it on a card and asking whether a competitor in an adjacent category could write the same sentence.
   If yes, the idea is too generic and needs sharpening.

4. Draft the logo system.
   Start from the wordmark or symbol, not from decoration.
   Specify the primary mark, the secondary or monogram mark used where the primary will not fit, the responsive sizes the mark must cover (favicon up through hero), and the dark-on-light and light-on-dark variants.
   Note the construction grid the mark sits on so future extensions stay coherent.
   Defer fine-grained logo construction to the dedicated logo-system skill if the brief calls for it.

5. Specify lockups.
   A lockup is the locked relationship of the logo to a tagline, sub-brand, product name, or partner mark.
   Define horizontal and stacked variants, the clear-space rule, and the minimum size.
   Forbid ad hoc lockups assembled by non-designers.
   Provide a small finite set of named lockups — for example primary, secondary, with-tagline, with-product-name, co-brand-horizontal — rather than a recipe that produces an unbounded number.

6. Define clear space and minimum size.
   Express clear space as a multiple of a glyph height or a logo-internal unit so the rule scales.
   Specify minimum sizes per medium — pixels for digital, millimeters for print — so the mark stays legible.
   Distinguish minimum legible (still readable) from minimum identifiable (recognizable as the brand even when the glyphs collapse) and call out which variant runs at each threshold.

7. Build the don't-use catalog.
   Enumerate the most likely abuses: rotation, color substitution, stretching, gradient overlays, drop shadows, placement on busy imagery, recoloring partner marks.
   Show each as a labeled negative example.
   A short, specific catalog beats a long generic one.
   Refresh the catalog from observed misuse during audits; abstract prohibitions are skimmed, concrete labeled negatives are remembered.

8. Build the primitive color ramp.
   For each hue the brand uses, define ten to twelve perceptually even stops.
   Include a neutral ramp at twelve to fourteen stops.
   Name primitives by hue and stop, not by usage — for example `blue-60`, `neutral-08`.
   Confirm the ramp is perceptually even rather than arbitrarily mixed; a uniform lightness step makes downstream pairing predictable.
   If the brand has a signature color, place it on the ramp and document which stop it occupies so derived shades and tints stay coherent.

9. Define semantic color roles.
   Layer named roles on top of the primitives: surface (default, raised, sunken, overlay), text (default, subtle, inverse, on-action), border (default, strong, focus), action (default, hover, pressed, disabled, on-action-text), feedback (success, warning, danger, info, with surface, text, and border variants per state).
   Every component-level color must trace to a semantic role, never to a raw primitive.
   The semantic layer is what survives a brand refresh; the primitive layer is what gets swapped.

10. Verify the accessibility floor on color.
    Compute contrast ratios for every named text-on-surface pair and every action-on-surface pair in both light and dark themes.
    Body text must clear 4.5:1; large text and UI components must clear 3:1.
    Where a brand color sits below the floor, define a tint or shade variant that meets it and reserve the original for non-text uses such as illustration accents, dividers, or decorative shape fills.

11. Specify a dark theme.
    Map every semantic role to a dark-mode primitive.
    Do not simply invert lightness — adjust saturation and elevate surfaces with bespoke neutrals.
    Confirm semantic roles, not primitives, are the swap targets.
    Audit shadows separately for dark mode; light-mode shadows usually disappear or look wrong on dark surfaces and need a separate scale.

12. Choose the type system.
    Pick a display family, a text family, and optionally a mono family.
    Confirm license terms cover the surfaces the brand needs (web, app, partner, print).
    Note fallback stacks and operating-system substitutes for environments where the licensed family cannot ship.
    Where the brand uses a single family for both display and text, confirm it has the weight and optical-size range that role demands.

13. Define the type scale.
    Choose a modular ratio or t-shirt scale.
    Cap the number of sizes at eight or nine to keep the system reasonable.
    Define line height alongside size, and define letter spacing wherever it changes perceptibly across sizes.
    Avoid leaving gaps in the scale that designers will fill with one-off sizes; a small gap-free scale produces fewer exceptions than a sparse one.

14. Specify responsive typography.
    Decide between tier-by-tier overrides per breakpoint, a fluid scale using `clamp()` or equivalent, or a hybrid.
    Confirm legibility at the smallest target size and at 200% browser zoom.
    State the rule for long-form text — usually a maximum line length (around 65 to 80 characters) — so the system protects readability rather than just defining sizes.

15. Define heading and prose patterns.
    Specify the role each size plays — display, h1 through h6, body, caption, label, code — and the recommended weight, color role, and letter spacing for each.
    Constrain weights to those the font file actually contains.
    Define how headings combine: an h1 followed by an h2 is common; an h1 followed by an h3 is a skip and should be discouraged.

16. Design the iconography family.
    Choose stroke vs. filled, the grid the icons are drawn on, the stroke weight, the corner radius family, and the optical-size buckets if the system needs more than one.
    Define a small icon-size token set (for example small, medium, large) rather than allowing raw pixel sizes.
    Specify the rule for sourcing icons that are not in the core set so contributions stay coherent — typically by commissioning new ones that match the family rather than mixing in third-party packs.

17. Direct photography.
    Decide whether the brand uses photography at all, and if so what kind — documentary, staged, abstract macro, product-on-seamless.
    Define lighting (hard, soft, ambient), color treatment (full color, monochrome, duotone), subject framing, and the rules for human representation including diversity, age, and depiction of work.
    Forbid stock imagery that violates the rules.
    Define the rule on AI-generated imagery — disclosure expectations, licensing of generated outputs, and contexts where it is forbidden.

18. Direct illustration.
    If illustration is part of the system, specify the line weight, the palette subset it uses, the level of abstraction, the use of texture, and the rules for combining illustration with photography or with the logo.
    Note any character or mascot policy: who draws the mascot, in what poses, with what expressions, and in what contexts the mascot does not appear.

19. Define motion principles.
    Choose a personality for motion — for example "decisive, calm, never decorative."
    Specify duration tokens (instant, fast, normal, slow, deliberate) and easing tokens (standard, emphasized, decelerate, accelerate).
    Define a reduced-motion alternative for every signature animation and confirm the system respects `prefers-reduced-motion`.
    Forbid motion that conveys information by motion alone; the static state must convey the same meaning.

20. Define voice and writing cues.
    Translate the personality words into a voice statement, a short list of words and phrases the brand prefers, a shorter list it avoids, and the rules on capitalization, contractions, numerals, oxford commas, and product-name treatment.
    Include a one-paragraph example of on-voice writing and one of off-voice for contrast.
    Examples teach voice better than abstract descriptors; budget the space.

21. Define accessibility commitments beyond color.
    State the WCAG level the system targets, the keyboard interaction model, focus-indicator tokens, alternative-text discipline for imagery, captioning expectations for motion, and reading-level targets for plain-language writing.
    Note any commitments above the floor — for example AAA for body text in a regulated product or plain-language scoring at a specific reading level.

22. Define sub-brand and co-brand rules.
    Specify how a product brand nests under the parent, what mark or lockup it uses, what color subset it can deviate into, and how partner marks combine with the primary mark.
    Forbid co-brand combinations that imply endorsement where none exists.
    Where a sub-brand needs visual distinction, give it a constrained accent color or a typographic treatment rather than letting it diverge across the system.

23. Map the system onto design tokens.
    List the token categories the system implies — color primitives, color roles, type, spacing, radius, shadow, motion — and the naming convention they will follow.
    The brand system is not a token system; it is the source from which a token system is generated.
    Confirm the handoff to a token pipeline is one-directional: brand spec changes propagate to tokens, never the other direction.

24. Define the source-of-truth artifact and its location.
    Decide whether the canonical system lives in a documentation site, a Figma library, a token JSON tree, or a combination, and which one wins when they disagree.
    Brand systems decay fast when there are two sources of truth and no rule.
    Name the team and the contact path for changes; without an owner the canonical drifts within a year.

25. Plan the rollout.
    List the surfaces in order — internal-facing first, partner-facing next, customer-facing last — and the migration path from any existing assets.
    Note the assets that are blocking and the ones that can be retired gradually.
    Schedule the rollout with enough lead time that partners can comply without emergency work.

26. Surface open questions.
    Almost every brief leaves decisions un-made.
    Collect them at the end with two or three options each and a recommended default.
    Forcing every decision into the first pass produces a brittle system; leaving none surfaced produces a vague one.
    Mark each open question with the latest date it must be resolved by, derived from the rollout schedule.

## Inputs

- A brief covering audience, category, competitive set, personality words, must-haves, and must-avoids.
- Existing assets (wordmark, hex codes, typeface licenses) if any.
- Surfaces the system must serve.
- Constraints — accessibility floor, parent-brand rules, trademark exclusions, license limits.
- Optional: maturity target — foundations only, full system, or full system with extensions.

## Outputs

- A layered specification covering logo, lockups, color primitives and roles, type, iconography, imagery direction, motion, and voice.
- A don't-use catalog and an accessibility floor.
- A list of design-token categories the system implies, with naming-convention guidance.
- A handoff plan to a token system, a guidelines site, or both.
- A list of open questions with options and recommended defaults.

## Examples

A request like "design a brand system for a developer-tools brand whose personality is precise, calm, and plain-spoken" should produce:
- A primary wordmark with a constrained monogram for favicons.
- A neutral-dominant palette with a single accent hue, both with twelve-stop ramps.
- Semantic color roles covering surface, text, border, action, and feedback in light and dark themes.
- A typographic system with one humanist sans for both display and text and one mono for code, with a t-shirt scale capped at nine sizes.
- An icon family at consistent stroke weight on a 24-unit grid.
- Motion principles favoring short durations and standard easing, with reduced-motion alternatives.
- A voice statement that forbids hype words and prefers active-voice prose.
- A contrast-floor audit confirming every named text-on-surface pair clears WCAG AA in both themes.

A request like "extend our existing wordmark into a system for a regulated-industry product" should:
- Preserve the wordmark as the primary mark and document its construction grid.
- Add semantic color roles that meet 4.5:1 across the board in both themes.
- Specify imagery rules that avoid implying clinical claims and forbid stock medical imagery.
- Define motion that respects reduced-motion preferences and avoids carrying meaning by motion alone.
- Add a voice cue list that forbids unsubstantiated efficacy language and requires plain-language reading-level targets.
- Map regulatory disclosures into the type and layout system so they appear consistently across surfaces.

## Anti-patterns to avoid

The methodology fails when any of these creep in. Flag them explicitly when reviewing a brand system.

- A palette of primitives only, with no semantic role layer. Every reskin becomes a search-and-replace project across components.
- A voice section made entirely of adjectives with no example paragraphs. Voice is taught by demonstration, not by descriptor lists.
- An icon set assembled from multiple third-party packs. Stroke weight, corner radius, and optical correction will not match, and the system will read as borrowed.
- A type scale with twelve or more sizes. Designers will pick whichever size looks right today and the result will read as inconsistent across surfaces.
- A motion system that names durations but not easing, or easing but not durations. The two travel together; specifying one without the other produces uneven motion.
- A dark theme produced by inverting lightness. Saturated brand colors become unusable, shadows disappear, and the result feels off without anyone being able to name why.
- A photography direction that says "authentic" without naming what authentic looks like. Authentic is the most-abused word in brand direction; replace it with concrete subject, lighting, and treatment rules.
- A guidelines document that is the only artifact. Without a token feed, an asset repository, and an audit cadence, the document is a museum piece.

## Handoff artifacts

The methodology produces a specification, not finished art. The downstream consumers need specific artifacts to do their work:

- A designer needs the construction grids, the optical-correction notes, and the source-typeface licenses.
- A token engineer needs the primitive ramps, the semantic role table, the type scale with named roles, and the motion duration and easing values.
- A guidelines author needs the don't-use catalog, the voice statement and examples, and the imagery direction.
- A partner-program owner needs the lockup rules, the co-brand permitted combinations, and the usage terms scope.
- An accessibility reviewer needs the WCAG target, the contrast audit, and the focus-indicator tokens.

Producing the specification without staging the handoffs leaves the system stranded.

## Limitations

- This skill produces a specification, not finished art. A designer or design partner is still required to produce the marks, type tests, and final assets.
- License compliance for typefaces, photography, and partner marks must be verified by a human with the rights and contracts in hand.
- Trademark availability of names and marks must be cleared by qualified counsel before any public use; the skill cannot perform a trademark search.
- The skill assumes the brief is honest. A brief that hides constraints (parent-brand rules, regulatory limits, embargoed launches, undisclosed parent-company guidelines) will produce an incoherent system that breaks on contact with reality.
- The skill assumes the brand owner has authority to commit. A system designed for a stakeholder who cannot sign off requires re-litigation each time it touches a new surface.
- Output should be reviewed by a brand owner before being treated as canonical, and by a qualified accessibility reviewer before being treated as compliant with any specific accessibility standard.
- Cultural appropriateness of imagery and language across the markets the brand will enter must be reviewed by humans with local context; the skill cannot detect culturally specific pitfalls reliably.

## What this skill does not do

To keep scope clear, the skill explicitly does not:

- Generate finished logo artwork. Logo construction belongs to a designer; the methodology states the system the logo will live inside.
- Pick specific hex codes for a brand. The methodology shapes the structure of the palette and the accessibility floor it must meet, leaving the aesthetic decision to a brand owner with the visual taste.
- Audit a token system in detail. A token-system critic is the right tool for token-level review; this skill produces the brand layer the tokens are generated from.
- Author the guidelines document. Use the guidelines-authoring skill for that; this skill produces the system the guidelines describe.
- Operate the asset pipeline. Use the asset-pipeline skill for that; this skill names the artifacts that will flow through the pipeline.
- Perform a trademark search or any other legal clearance.

## Sources reviewed

- https://brand.github.com/ (proprietary; trademarks not used as anchors in body)
- https://github.com/sturobson/brand-resources (MIT)
- https://github.com/jcklpe/open-source-branding-toolkit (CC-BY-SA family per repo)
- https://github.com/finos/branding (CDLA-Permissive)
- https://github.com/knative/community/blob/main/BRANDING.MD (CC-BY 4.0)
- https://design.gitlab.com/ (CC-BY-SA 4.0)
- https://carbondesignsystem.com/elements/color/overview/ (Apache-2.0 system; brand prose CC-BY)
- https://github.com/VoltAgent/awesome-design-md (MIT)
- https://github.com/18F/content-guide (CC0 / public domain)
- https://www.patternfly.org/ux-writing/brand-voice-and-tone/ (MIT)
