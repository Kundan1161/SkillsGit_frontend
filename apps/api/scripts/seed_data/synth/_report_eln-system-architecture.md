# Wave-4 Methodology-Recovery Report — ELN System Architecture

**Niche:** biotech — Electronic Lab Notebook (ELN) system architecture
**Agent wave:** 4 (methodology-recovery)
**Date:** 2026-05-14
**Curator account at publish time:** @skillsgit-curated
**License posture:** all three skills published as `license_type: free`

## Skills produced

Three skills, all in `D:\skillsgit\apps\api\scripts\seed_data\synth\`:

1. `eln-system-architect.skills.md` — End-to-end ELN architecture
   methodology: entity model, immutability and amendment semantics,
   audit-trail design, permissions and signature authority,
   integration surface, storage and archival, and a regulatory
   readiness ladder.

2. `eln-21cfr-part11-readiness.skills.md` — Gap-analysis methodology
   for assessing an ELN against 21 CFR Part 11 expectations across
   seven domains: unique user identity, electronic-signature
   semantics, audit-trail integrity, controlled access and segregation
   of duties, system validation, training and procedures, and ongoing
   operational practice.

3. `eln-instrument-integration-architect.skills.md` — Integration
   architecture for instrument and analysis-software data flowing
   into an ELN: instrument inventory and tiering, ingestion topology,
   per-instrument adapter shape, raw-versus-processed separation with
   lineage graph, failure-mode register, and the notebook ingest
   contract.

All three carry the mandatory regulated-environment disclaimer as a
blockquote immediately under the title, per spec.

## Sources reviewed and licenses

The following sources were read during the survey. None were copied,
quoted, or close-paraphrased. Each is cited in the `## Sources
reviewed` section at the foot of every skill it informed, generically
as "ELN system" with the license tag — product names are not used in
skill body prose, only in the sources section.

| Source | License | Role in synthesis |
|---|---|---|
| eLabFTW project repository | **AGPL-3** | Multi-team self-hosted ELN; informed audit-trail, trusted-timestamping, and resources-database patterns. Read and cited only. |
| SciNote ELN repository | **MPL-2.0** | Life-science notebook with project / experiment / task / protocol hierarchy; informed the project-layer recommendation and role pattern. |
| Chemotion ELN repository | **AGPL-3** | Chemistry-focused notebook with samples / reactions / wellplates / analyses as first-class entities; informed the optional-entity expansion and the analysis-attached-to-sample pattern relevant to lineage. Read and cited only. |
| RSpace open-source platform repository | **AGPL-3** | Notebook plus inventory with auditability emphasis; informed the inventory coupling and the audit posture. Read and cited only. |
| Indigo ELN v2 repository | **MIT** | Chemistry notebook with a separate signature module and chemical-registration service; informed the "signature service as a separate component" and the "adapter services rather than embedded drivers" patterns. Closer reuse permitted but still no prose copied. |
| US 21 CFR Part 11 (eCFR) | Public regulation | Anchored every expectation in the Part 11 readiness skill. |
| FDA Part 11 scope-and-application guidance | Public guidance | Framed the risk-based posture and the conservative readiness language. |
| EU EudraLex Annex 11 | Public regulation | Cross-frame contrast in the Part 11 skill's out-of-scope and target-frame inputs. |
| ALCOA+ data-integrity guidance (public regulatory writings) | Public guidance | Framed raw-vs-processed separation and lineage in the instrument-integration skill. |

## Methodology vs. expression boundary — checks performed

The AGPL constraint is the load-bearing issue for this niche; three of
the five ELN repos surveyed are AGPL-3. The following checks were
applied to keep the output on the methodology side of the line:

1. **No product names in body prose.** Search of the three skill
   bodies confirms no occurrences of the strings `eLabFTW`, `SciNote`,
   `Chemotion`, `RSpace`, or `Indigo` outside the `## Sources reviewed`
   section. Bodies refer generically to "ELN system", "the notebook",
   "the system".

2. **No code, schemas, or filenames lifted.** None of the entity-model
   sections name tables, columns, or class names from any source.
   Entity names used (`User`, `Team`, `Project`, `Experiment`,
   `Protocol`, `Sample`, `Attachment`, `Signature`, `Audit event`) are
   the *generic vocabulary of the field* and predate every cited
   project; they appear in textbooks, ISO 17025 vocabulary, and FDA
   guidance. Chemistry-specific additions (`Reaction`, `Wellplate`,
   `Analysis`) are likewise generic discipline vocabulary.

3. **No close paraphrase of README or doc text.** Source READMEs were
   read once via WebFetch with summary prompts and not retained. The
   skill bodies were authored from a synthesized mental model of the
   field, not from sentence-by-sentence rewriting of any single source.

4. **Architectural patterns described, not implementations.** The
   readiness skill describes Part 11 expectations from the regulation
   itself, not from any vendor's compliance claims page. The
   instrument-integration skill describes patterns (file-watcher,
   adapter-as-client, content-addressed storage) that are common
   across LIMS, ELN, scientific-data-management, and general
   data-engineering literature — not implementations of any one ELN.

5. **AGPL sources cited with the tag.** Every AGPL source carries
   `(AGPL-3)` in the sources list; the MIT source carries `(MIT)`; the
   MPL source carries `(MPL-2.0)`. Per policy, AGPL is read-and-cite
   only.

6. **Distinct from existing `lab-notebook-discipline` skills.** The
   existing `batch-record-author` skill (and the report
   `_report_lab-notebook-discipline.md`) covers *practice* — how a
   scientist composes a batch record. This wave covers *system
   architecture* — how the platform that holds those records is
   designed, assessed, and integrated. No overlap with discipline-side
   guidance.

## Patterns abstracted across the field

The skills crystallise the following recurring patterns observed
across the surveyed systems and the regulatory text:

- **Small, named core entity set.** Every coherent ELN converges on
  some variant of {user, team, project, experiment, protocol, sample,
  attachment, signature, audit event}. Discipline adds optional
  entities (reaction, wellplate) without changing the spine.

- **Locked-then-amended record model.** A draft phase with free
  editing, a clearly defined locking event, and an amendment model
  that is either append-only addendum or versioned-record. The two
  amendment models are mutually exclusive and must be picked.

- **Audit trail as a subsystem, not a log.** Append-only at storage,
  not application; periodic external hash-chain or timestamp; readable
  by scientists; retention tied to the record retention horizon.

- **Signature meaning beyond "sign".** Authored, reviewed, witnessed,
  approved. Different roles, different rules (witness cannot be
  author). Signature events are bound to a record state, not to the
  record id.

- **Permissions as roles plus per-record sharing plus signature
  authority.** Three orthogonal axes; conflating them into one
  permission table produces the field's most common security gaps.

- **Adapter pattern for integrations.** Notebook exposes a small
  stable ingest API; vendor-specific code lives in adapter services;
  no driver code in the core. This pattern shows up in every system
  that has survived more than one vendor upgrade.

- **Raw versus processed as a lineage graph, not a flag.** The most
  durable lab-data architectures store raw and processed as separate
  artefacts with explicit parent / child relationships; "edit in
  place" is the modal source of integrity failure.

- **Readiness as a ladder, not a switch.** Research deployment,
  GLP-aligned deployment, Part 11-ready deployment. Movement up the
  ladder is procedure and evidence, not rewrite — provided the
  architectural primitives were installed at the start.

## Confidence assessment

- **eln-system-architect — high confidence.** Entity model, lifecycle,
  audit, permission, and integration patterns are well-established
  across the surveyed open-source field, regulated-systems literature,
  and ISO 17025 vocabulary. The skill stays at the architectural
  abstraction layer where the field has clear consensus.

- **eln-21cfr-part11-readiness — high confidence on framework,
  medium-high on practical gap pattern.** The seven domains map
  cleanly to the published text of 21 CFR Part 11 and the FDA scope
  guidance. The "common gaps" lists are conservative and reflect
  patterns repeatedly noted in public Part 11 commentary; specific
  deployments may show different gap patterns. The mandatory
  disclaimer steers the output away from compliance pronouncements
  that this skill cannot make.

- **eln-instrument-integration-architect — high confidence on
  patterns, medium on tier-C specifics.** Ingestion topologies,
  adapter shape, content-addressed storage, raw/processed lineage,
  and failure-mode patterns are stable across LIMS, ELN, and broader
  scientific-data-management practice. Vendor SDK specifics
  (which would be the Tier-C details) are out of scope by design —
  they shift faster than a methodology skill can usefully chase, and
  the skill explicitly defers them.

- **Niche differentiation from `lab-notebook-discipline` — clean.**
  The earlier wave's lab-notebook skills describe the *user-side*
  practice of recording science (batch records, contemporaneous notes,
  data integrity at the bench). This wave's skills describe the
  *platform-side* architecture that holds those records. The two
  bodies of work compose; they do not collide.

## Frontmatter and body compliance

- All three skills carry the required first-tag `niche:eln-system-architecture`.
- All three carry `category: biotech`.
- All three carry `license_type: free` per policy.
- Each frontmatter has 7 tags (within the 4-7 spec window for "others"
  after the niche tag).
- Bodies range from approximately 320 to 410 lines, inside the
  300-600-line spec window.
- Each body opens with the mandatory regulated-environment disclaimer
  as a blockquote, with wording adapted per skill so that it is
  topical rather than copy-pasted.
- Each body contains the required `## When to use` and `## How to apply`
  sections plus the recommended `## Inputs`, `## Outputs`,
  `## Examples`, `## Limitations`, and `## Sources reviewed` sections.

## Open follow-ups (not in scope this wave)

- A companion *ELN deployment runbook* skill (operations side: backup
  drills, audit-trail review cadence, account-review procedures) would
  complete the operational ladder.
- A *LIMS-versus-ELN scoping* skill for organisations that have both
  and need to decide which system owns which entity, especially around
  sample identity and inventory.
- A *vendor ELN evaluation rubric* skill that consumes the
  architectural model from `eln-system-architect` and scores commercial
  products against it.
