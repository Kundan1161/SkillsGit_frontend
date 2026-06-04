---
id: skillsgit-curated/brand-asset-pipeline
version: 1.0.0
name: Brand Asset Pipeline Architect
description: Architect a brand asset pipeline — source-of-truth repository, naming conventions, derivative generation automation, partner distribution with rights metadata, retirement of old marks, and audit cadence.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: creative
tags: [brand-visual-identity, asset-pipeline, naming-conventions, asset-distribution, dam, asset-versioning]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - brand asset pipeline
  - asset library
  - asset repository
  - asset naming
  - asset distribution
  - asset retirement
  - dam
  - asset versioning
  - derivative generation
  - brand audit
example_invocations:
  - "Architect the asset pipeline that turns our master logos into web, print, and favicon derivatives."
  - "Set up naming conventions and folder layout for our brand asset repository."
  - "Plan partner distribution of brand assets with rights metadata."
  - "Build a retirement plan for our outgoing logo and an audit cadence for the new one."
inputs:
  - name: asset_scope
    type: text
    required: true
    description: The scope of assets covered — for example "logos, lockups, icons, photography, illustration, motion, templates, color profiles." Include current asset locations if known.
  - name: distribution_channels
    type: text
    required: false
    description: Where assets must reach — for example "marketing site, product UI, partner portal, press, conference vendors, merchandise vendors."
  - name: pipeline_constraints
    type: text
    required: false
    description: Constraints on the pipeline — for example "must use existing DAM, must integrate with Figma, must produce print-ready PDFs, must support self-serve partner downloads."
  - name: governance
    type: choice
    required: false
    description: The governance model the pipeline must support.
    choices: [open-self-serve, gated-internal, partner-licensed, hybrid]
outputs:
  - name: pipeline_design
    type: markdown
    description: The pipeline architecture — source of truth, generation flow, distribution channels, and metadata model.
  - name: conventions
    type: markdown
    description: Naming, folder layout, version-tagging, and rights-metadata conventions.
  - name: operating_runbook
    type: markdown
    description: Runbook for onboarding new assets, generating derivatives, distributing to partners, retiring outgoing marks, and auditing usage.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Reach for this skill when an agent is asked to design or document the operational pipeline behind a brand asset library. Typical situations:

- A brand has grown past the point where assets live in someone's Drive folder and needs a real repository, a real pipeline, and real conventions.
- A brand owner is replacing a digital asset management product or unifying several scattered libraries into one.
- A partner program is launching and the team needs self-serve asset distribution with rights metadata.
- A logo refresh is underway and the team needs a coordinated retirement and rollout plan for thousands of derivative files in circulation.
- A brand audit has shown that on-the-ground use has drifted from the canonical assets, and the team needs an audit cadence with teeth.

Skip this skill when the request is to design the brand system itself, when the request is to author the guidelines document, when the request is to construct a single logo system (use the dedicated skills), or when the request is to evaluate a specific DAM product. This skill produces a pipeline architecture and conventions, not a tool selection.

## How to apply

Work through the architecture and operations in this order. The first eight steps establish the data model; the rest are flows and operations.

1. Identify the asset categories the pipeline must serve.
   The common categories are logos and lockups, icons, photography, illustration, motion (video, animated GIF, Lottie), audio if relevant, templates (decks, social, email), and source files for each.
   Note any category that needs specialty handling such as print-ready PDFs or platform-specific app icons.
   Distinguish assets that the pipeline owns from assets that the pipeline merely indexes (a partner's logo, for example, is referenced but not regenerated).

2. Choose the source-of-truth repository.
   Common choices are a Git repository for assets that are file-based and reviewable through pull requests, a DAM product when search and rights metadata matter more than versioning, a Figma library when designers are the primary contributors and the canonical lives in the editor, or a hybrid in which a Git repo holds source vector files and a DAM holds curated derivatives.
   One repository wins as canonical when there is disagreement; the others mirror.
   State the rule explicitly in the operating documentation.

3. Decide on a single canonical artifact per asset.
   Each asset has one master file in vector or in highest-fidelity raster, and every other file derives from it.
   Forbid the practice of editing derivatives in place; edits go to the master and the derivatives regenerate.
   Without this rule, the library drifts within months and audits become unenforceable.

4. Define the folder layout.
   A layout that scales is shallow at the top and deepens by usage rather than by file format.
   A pattern like `marks/`, `lockups/`, `icons/`, `imagery/`, `motion/`, `templates/`, `archive/`, with category sub-folders inside, lets browsing work.
   Forbid format-first folders (`png/`, `svg/`); the same asset in three formats belongs together.
   Document the layout in a README at the repository root so contributors do not invent new top-level folders.

5. Define the naming convention.
   A filename encodes brand or product, asset family, variant, color treatment, theme, and aspect or size.
   A pattern like `acme-mark-primary-full-onlight.svg`, `acme-lockup-vertical-mono-ondark.pdf`, `acme-favicon-32.png` reads at a glance and sorts predictably.
   Use lowercase, kebab-case, no spaces, no special characters.
   State the convention and apply it without exceptions; exceptions are the source of pipeline failures.

6. Define version tagging.
   Asset versions are not semver — they are sequential or date-tagged.
   A convention like `acme-mark-primary-full-onlight.v3.svg` or a tag in repository metadata (Git tag, DAM version field) tracks the version.
   Confirm that derivatives carry the same version as their master and that a regeneration bumps every derivative together.
   Tagged releases let consumers reference a stable version rather than the moving head.

7. Define the rights metadata model.
   Each asset carries metadata: owner, license, permitted uses (internal, partner, public), forbidden uses, expiry date if any, third-party rights (photographer, illustrator, font license), and notes.
   Without rights metadata, partner distribution and audit are guesswork.
   The metadata lives alongside the file (sidecar JSON, repository commit message tags, DAM field) and travels with it.
   Where third-party rights expire, the pipeline must alert the brand owner before the expiry rather than after.

8. Define a unique asset identifier.
   Each asset has an immutable identifier independent of its filename.
   The identifier is what derivatives refer to, what distribution logs record, and what audit references.
   Filenames can change; identifiers do not.
   Choose a scheme that does not collide on rename or move — a UUID, a hash of original content, or a sequential identifier in a registry.

9. Set up the derivative generation pipeline.
   Master vector files generate cleaned SVG, raster PNG sets at standard sizes, PDF-X with print color profiles, EPS for legacy vendors, favicon and app-icon bundles, and any other derivatives the channels need.
   The pipeline is a script or a job, not a manual export task.
   Confirm that the pipeline is idempotent: running it twice produces identical files, byte-for-byte where the format allows.
   Run the pipeline in CI to verify regeneration matches the committed derivatives; drift is caught at PR time rather than in production.

10. Set up SVG cleaning.
    Hand-edited SVGs carry editor metadata, hidden layers, and unused elements that bloat files and break consumers.
    The pipeline strips comments, removes unused groups, sets a canonical viewBox, embeds title and description for accessibility, and minifies.
    Run a validator that flags non-conforming SVGs at PR time.
    Confirm the cleaned SVG renders identically to the source; aggressive optimization sometimes drops detail.

11. Set up raster generation.
    PNG derivatives generate at canonical sizes (sixteen, thirty-two, forty-eight, sixty-four, one hundred and twenty-eight, two hundred and fifty-six, five hundred and twelve, one thousand and twenty-four, two thousand and forty-eight for digital scaling).
    Each size renders from the vector source at its target dimension; do not scale a single rasterization.
    App icons render at platform-specific sizes from masters designed at those sizes where optical correction differs.

12. Set up print derivative generation.
    PDF-X carries the documented CMYK color profile and embedded fonts (or outlined text).
    Confirm spot-color tagging where the print job uses spot inks.
    State the conversion rule when a vector source must be reproduced in CMYK; usually the print vendor performs the conversion using the documented profile, but the conversion target must be stated to avoid mismatched results.

13. Set up favicon and app-icon bundles.
    The favicon bundle includes SVG, ICO with legacy sizes, PNG at high resolution for modern browsers, Safari pinned-tab mono variant, and the manifest entries that reference them.
    The app-icon bundle includes iOS rounded masters, Android adaptive layers (foreground, background, monochrome), and Windows tile sizes.
    Each bundle has its own manifest with version, generation timestamp, and source identifier.

14. Define the canonical color profiles.
    sRGB for web.
    CMYK with a documented profile (FOGRA39, GRACoL 2013, or as required) for print.
    Display-P3 where wide-gamut surfaces are supported.
    Document the profile per channel and per asset so vendors know which to use.
    Confirm the master color values are stored in a profile-independent form (Lab, OKLCH) where the system supports it, so derivative conversions are deterministic.

15. Set up the contribution flow.
    New assets enter through a documented path — a pull request to a Git repository, an upload to a DAM with required metadata, a publish from a Figma library through an export job.
    Define the review checklist (naming convention, metadata complete, rights cleared, optical at small sizes confirmed, derivatives generate successfully) and require sign-off before merge or publish.
    The reviewer is named in the operating runbook; reviews that drift to whoever is around degrade in quality.

16. Set up the distribution channels.
    Internal distribution is the company-facing portal or repository — open to staff, search-indexed, with a documented "how to find the right file" rule.
    Partner distribution is a gated portal with sign-in and accepted terms, surfacing only the partner-permitted variants and stamped with the partner's license metadata.
    Press distribution is a public page with logos, headshots, and a fact sheet, downloadable without sign-in but governed by the usage terms.

17. Set up the watermark and audit-trail policy.
    When assets are distributed to partners, the distribution log records the partner identifier, the asset identifier, the version, the timestamp, and the license terms accepted.
    For high-stakes assets, optional invisible watermarks (steganographic or pixel-level for raster, metadata-level for vector) let the audit identify the source of a leak.
    State the policy clearly and notify partners; covert watermarking damages trust if discovered after the fact.

18. Set up integration with the product.
    Product surfaces that consume brand assets — the marketing site, the product UI, partner widgets — should reference assets by canonical identifier, not by copying files into product repositories.
    Where copying is unavoidable, a build-time job pulls the canonical version.
    Forbid hand-copied logo files in product repositories; they go stale within a release cycle and audit cannot find them all.

19. Set up integration with templates.
    Templates for decks, social, email, and document covers consume canonical assets.
    The template-build pipeline embeds the current versions, and template re-builds happen automatically when a referenced asset version changes.
    Note which fields in each template are editable and which are locked to canonical values.

20. Plan retirement of outgoing marks.
    When a new mark lands, the old mark is in circulation everywhere.
    Stage retirement: announce the new mark with a date past which it is canonical, set retirement dates per surface (digital first, then print, then partner-distributed, then merchandise), notify partners with enough lead time, and move retired masters to an `archive/` folder with a clear status flag.
    Do not delete archives; legal and audit need them.

21. Plan the audit cadence.
    Quarterly is reasonable for digital surfaces (marketing site, product UI, partner widgets), annual for print and partner-produced collateral, and event-driven for any reported misuse.
    The audit scans for files that do not match the canonical version, files that violate the don't-use catalog, and partner distributions that have exceeded their license.
    Feed every confirmed misuse back into the don't-use catalog so future audits become more concrete.

22. Plan governance and ownership.
    Name the team that owns the pipeline, the on-call rotation if any, the escalation path for unusual partner requests, the approval flow for new assets entering the canonical, and the rule for accepting contributions from outside the brand team.
    Without ownership, the pipeline rots within a year.
    A named owner with budget is the difference between a working pipeline and a graveyard repository.

23. Plan the metrics.
    The pipeline emits metrics worth tracking: time from new-asset request to canonical publish, partner-portal download counts by asset, audit-finding counts per quarter trending toward zero, percentage of product surfaces consuming canonical references rather than copies.
    These metrics surface drift before it becomes a crisis.

24. Plan failure modes.
    The common failures are master-file corruption (mitigated by repository backups and tagged releases), pipeline drift (mitigated by idempotent generation and a CI check that regenerated derivatives match committed ones), partner misuse (mitigated by audit and license enforcement), and silent retirement (mitigated by notification leadtimes and a retired-asset banner during the transition window).

25. Plan accessibility for the pipeline itself.
    The asset portal must be navigable by keyboard, the search must surface assets by description not just by filename, and downloadable assets must include alt-text guidance and accessibility metadata where relevant (logo titles in SVG, captions for motion).
    The pipeline that distributes accessible assets must itself be accessible to operate.

26. Produce the deliverables.
    The methodology outputs the pipeline architecture, the naming and metadata conventions, the contribution and distribution flows, the retirement and audit plans, the governance model, and the runbook for operating it.

## Anti-patterns to avoid

The methodology fails when any of these creep in. Flag them explicitly when reviewing a pipeline.

- Hand-edited derivatives. The moment someone edits a PNG in place, the master is no longer the source of truth and audit is broken.
- A naming convention with exceptions. Every exception accumulates and the convention stops being load-bearing.
- A partner portal with no audit log. Misuse cannot be traced back to a source and the brand owner loses the leverage to enforce.
- A retired-mark folder that is deleted. Legal and audit need the history; the cost of storage is trivial compared to the cost of losing the record.
- A pipeline that runs only when the brand team remembers to run it. Automate or it does not exist.
- A canonical repository with no backups. A single corruption event takes down the brand.
- Rights metadata that is optional at contribution time. Optional metadata is missing metadata; require it at PR or upload time.
- Product surfaces that hand-copy assets rather than referencing canonical. Within two releases the copies drift and the brand drifts with them.

## Inputs

- The asset scope to be covered.
- The distribution channels assets must reach.
- Constraints on tools and integration.
- Optional: the governance model the pipeline must support.

## Outputs

- Pipeline architecture with source-of-truth and derivative-generation flow.
- Naming, folder, version, and rights-metadata conventions.
- Contribution and distribution flows with review checklists.
- Retirement and audit plans.
- Governance model and operating runbook.

## Examples

A request like "architect the asset pipeline for a developer-tools brand whose canonical is a Git repository and whose distribution targets are a product UI, a marketing site, a partner portal, and a press page" should produce:
- A Git-canonical model with SVG masters under version tags.
- An idempotent generation job that produces SVG, PNG sets, PDF-X, and favicon bundles, run in CI on every PR.
- A build-time integration that pulls canonical assets into product repositories by version reference.
- A partner portal gated on signed terms with distribution logging keyed to partner identifier.
- A press page with logos, headshots, and a fact sheet downloadable without sign-in.
- A quarterly audit job that scans product surfaces and partner widgets for drift from the canonical version.
- A documented runbook for onboarding new assets, with a review checklist and a named reviewer rotation.

A request like "plan the retirement of our previous logo and the rollout of the new one across product, marketing, partners, and merchandise" should produce:
- A phased schedule with digital surfaces first (week one to week four), marketing surfaces second (week four to week twelve), partners third (week four to week twenty-four with sixty to ninety days of notice), and merchandise last (existing inventory sells through, new inventory uses the new mark).
- Partner notifications with sixty to ninety days of lead time and a clear cutoff date.
- A merchandise sell-through allowance for unsold inventory with a documented end date.
- Archive of the previous master files under a status flag indicating retired.
- A transition banner on the asset portal during the rollout window pointing to the new mark.
- An audit plan for the first quarter after rollout to catch surfaces that did not migrate.

## Limitations

- The skill produces a pipeline architecture and conventions; it does not select or implement a specific tool or DAM product. Tool selection requires evaluation against the brand owner's existing stack, budget, and security requirements.
- Rights metadata, partner licenses, and watermark policies have legal implications and must be reviewed by qualified counsel before public use.
- Audit findings and retirement schedules are operational commitments; partners and vendors must be consulted on lead times, and contractual notice periods may govern.
- The skill assumes a brand owner with authority to enforce conventions. Without ownership and budget, no pipeline survives the first year.
- The skill does not handle DAM product migration. Migrating from one product to another is a project in its own right and requires its own plan.
- Output should be reviewed by a brand owner, a system owner, and for licensed assets by counsel before being treated as canonical.

## What this skill does not do

To keep scope clear, the skill explicitly does not:

- Design the brand system. Use the brand-system-architect skill for that.
- Author the guidelines document. Use the brand-guidelines-authoring skill for that.
- Construct the logo system. Use the logo-system-construction-methodology skill for that.
- Select a specific DAM product or implement a specific Git workflow. Tool selection is the brand owner's choice; the methodology produces the conventions any tool can implement.
- Author partner license agreements. Counsel drafts the agreements; the pipeline enforces them.
- Conduct a forensic investigation of a brand leak. Pipeline metadata supports an investigation but the investigation itself is a separate operation.

## Operating runbook outline

The methodology produces a runbook that the operating team uses day to day:

- How to onboard a new asset: contribution path, required metadata, review checklist, sign-off.
- How to regenerate derivatives: trigger, expected outputs, validation step.
- How to distribute to a partner: portal entry, license stamping, audit log entry.
- How to retire an asset: archive move, status flag, notification list.
- How to handle a misuse report: triage, evidence collection, contact path, follow-through.
- How to run a quarterly audit: scope, scan tools, findings template, follow-through.
- How to back up the canonical repository: schedule, retention, restore drill cadence.
- How to escalate an unusual partner request: contact path, decision criteria, response template.
- How to onboard a new partner: terms acceptance, asset bundle, audit-log entry, notification of the brand owner.
- How to handle a third-party rights expiry: alert window, decision to renew or replace, retirement of dependent assets.
- How to handle a security incident touching the canonical repository: containment, brand owner notification, audit trail preservation, restore from backup.
- How to retire a partner: revoke portal access, freeze license, archive the partner's distribution log, retain log for the retention period stated in the license terms.

## Sources reviewed

- https://github.com/sturobson/brand-resources (MIT)
- https://github.com/finos/branding (CDLA-Permissive)
- https://github.com/knative/community/blob/main/BRANDING.MD (CC-BY 4.0)
- https://github.com/open-life-science/branding (CC-BY 4.0)
- https://github.com/jcklpe/open-source-branding-toolkit (CC-BY-SA family per repo)
- https://design.gitlab.com/ (CC-BY-SA 4.0)
- https://github.com/VoltAgent/awesome-design-md (MIT)
- https://brand.github.com/ (proprietary; trademarks not used as anchors in body)
- https://github.com/stillwwater/UnityStyleGuide (MIT)
