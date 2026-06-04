---
id: skillsgit-curated/eln-system-architect
version: 0.1.0
name: ELN System Architect
description: Design an electronic lab notebook system end-to-end — entity model, immutability and amendment semantics, audit trail, permissions, integrations, and archival.
authors:
  - name: Wave-4 Methodology-Recovery Agent
    handle: synth-bio
    role: author
category: biotech
tags:
  - niche:eln-system-architecture
  - electronic-lab-notebook
  - entity-model
  - audit-trail
  - immutable-records
  - permissions
  - archival
license_type: free
ai:
  required_models:
    - claude-opus-4-7
  compatible_models:
    - claude-sonnet-4-6
    - gpt-4o
  min_context_tokens: 40000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - electronic lab notebook
  - ELN architecture
  - lab notebook system design
  - experiment record model
  - lab data management
  - notebook entity model
  - witness signature design
  - laboratory information architecture
example_invocations:
  - "Design the entity model for a multi-team electronic lab notebook used by a biotech of 80 scientists."
  - "Help me architect immutable experiment records with a clean amendment workflow."
  - "What does a defensible audit trail look like for a lab notebook system before any regulated work?"
inputs:
  - name: organisation_profile
    type: text
    required: true
    description: Size of the lab, number of teams, scientific domains, and whether work is purely research or trending toward regulated use.
  - name: deployment_model
    type: choice
    required: false
    description: Preferred deployment posture.
    choices:
      - single-tenant-self-hosted
      - multi-tenant-shared
      - cloud-managed
      - hybrid
  - name: integration_surface
    type: text
    required: false
    description: Instruments, inventory systems, identity providers, or analysis pipelines the notebook must talk to.
outputs:
  - name: eln_architecture_document
    type: markdown
    description: Layered architecture brief covering entity model, permission model, audit-trail design, integration points, and an archival strategy, with deliberate gaps highlighted for follow-up.
changelog:
  - version: 0.1.0
    date: 2026-05-14
    notes: Initial synthesis. Methodology distilled from a survey of widely deployed open-source ELN systems; no proprietary text reused.
---

# ELN System Architect

> **Mandatory disclaimer.** This skill produces methodology guidance for
> electronic lab notebook (ELN) system architecture. Regulated
> environments (GLP, GMP, FDA 21 CFR Part 11, EU Annex 11, ISO 17025)
> impose specific record-keeping, audit-trail, and electronic-signature
> requirements. Compliance for any regulated workflow must be reviewed
> by qualified Quality and Regulatory staff. Use the output of this
> skill as an architectural starting point, not as a validated design.

## When to use

Invoke this skill when a team is about to build, evaluate, customise, or
replace an electronic lab notebook and needs an architectural narrative
that holds together rather than a feature checklist. Typical prompting
situations:

- A growing research group is outgrowing shared drives and paper
  notebooks and wants a clean entity model before committing to a tool.
- A platform team is being asked to "make our ELN ready for regulated
  work" and needs to draw the line between today's research deployment
  and a future controlled one.
- A vendor is being assessed and the buyer needs an internal yardstick
  for what the system should actually contain.
- An in-house notebook needs a redesign because its data model has
  drifted (free-text fields holding sample IDs, attachments without
  lineage, no concept of an immutable record).

This skill stays at the architecture layer. It does not write code or
endorse any particular product. Lab discipline (how scientists *use* the
notebook) is covered by separate skills.

## How to apply

Work through the following passes in order. Each pass produces a named
section in the final deliverable.

### 1. Capture the operating context

Ask, and record explicitly:

- **Scientific scope** — wet-lab biology, analytical chemistry, formulation,
  process development, bioinformatics dry-lab, or a mix. The dominant
  scope drives the central entity (experiments vs. reactions vs. runs).
- **Organisational shape** — number of teams, whether teams are isolated
  silos or share inventory and protocols, expected user count over
  three years.
- **Regulatory trajectory** — research-only today, GLP-adjacent tomorrow,
  ever expected to support GMP or 21 CFR Part 11 records. Architectural
  decisions made now will be expensive to retrofit later.
- **Existing data** — what must be migrated in (legacy notebooks, LIMS
  exports, shared drives) and what stays where it lives.
- **Failure cost** — what happens if a notebook entry is lost, altered,
  or attributed to the wrong scientist.

Surface unknowns in a dedicated "Open questions" subsection. Do not let
ambiguity disappear into prose.

### 2. Fix the core entity model

Every coherent ELN architecture revolves around a small set of nouns.
Pick them deliberately and define each one before moving on.

The minimum viable set:

- **User** — a real, named person. Service accounts are a separate
  subclass and must be marked as such; they should never appear in a
  signature field.
- **Team** (or workspace, group) — the unit of permission inheritance
  and the boundary for sharing protocols and inventory.
- **Project** — a long-lived container that groups experiments toward a
  scientific objective. Optional but recommended; otherwise experiments
  drift into a flat list that becomes unsearchable past year two.
- **Experiment** (the central record) — a dated, owned, append-only
  account of scientific work. Title, hypothesis, procedure, results,
  attachments, links to inventory, status, signatures.
- **Protocol** (or template) — a reusable procedure that an experiment
  can be instantiated from. Versioned. An experiment records *which*
  version of the protocol it followed.
- **Sample** / **Item** — a tracked physical thing: a tube, a plate, a
  cell line aliquot, a chemical bottle, a reagent lot. Has identity,
  location, parentage, and a chain of custody.
- **Attachment** — any file (image, instrument output, spreadsheet,
  PDF). Stored by content hash, never by name alone.
- **Signature** — a cryptographically and procedurally bound assertion
  that a named user attests to a specific record state at a specific
  time, with a stated meaning (authored, witnessed, reviewed, approved).
- **Audit event** — an append-only log entry capturing who, what, when,
  before, after, and why.

Optional but common additions for richer domains:

- **Reaction** (chemistry) — a specialised experiment with reactants,
  products, stoichiometry, and yield.
- **Wellplate / Run / Batch** — high-throughput parents that group many
  child measurements.
- **Analysis** — derived results attached to a sample or experiment,
  with a pointer to the source raw file.
- **Inventory location** — freezer, shelf, box, position. A graph, not a
  string.

For each entity, write down:

1. Primary identifier (system-generated, opaque, never reused).
2. Ownership (which user, which team).
3. Lifecycle states it can occupy.
4. Which relationships are mandatory vs. optional.

Draw the entity diagram. Resist the urge to merge "experiment" and
"protocol" into one polymorphic blob; they have different lifecycles.

### 3. Define the record lifecycle and immutability rule

This is the architectural crux. Decide explicitly:

- **Draft phase.** While an experiment is *in progress*, free editing is
  expected. The audit trail still records changes but the record itself
  is mutable.
- **Locking event.** A clearly defined action (author submits, witness
  signs, status transitions to "complete") that freezes the record
  state. After locking, the canonical body MUST NOT be silently
  modifiable.
- **Amendment model.** Real labs need to correct mistakes. Choose one:
  - **Append-only addendum** — original record stays untouched, an
    addendum block is added with its own signature and reason.
  - **Versioned record** — each lock produces a new immutable version;
    the chain of versions is preserved with diffs and reasons.
  The append-only addendum model is operationally simpler; the
  versioned model fits chemistry workflows where reactions are
  iterated. Pick one and apply it consistently.
- **Deletion policy.** Locked records are never deleted from storage.
  "Deletion" is a soft state transition (withdrawn, retracted) with a
  recorded reason. Hard purges exist only for legal-hold workflows
  and require dual authorisation.

Document the state machine as a diagram. Every transition must be a
named, audited event.

### 4. Design the audit trail

The audit trail is its own subsystem, not a debug log.

Required properties:

- **Append-only at the storage layer.** Application-level append is not
  enough. Use a database design that prevents updates and deletes on
  the audit table (e.g., revoke privileges, write-once volumes, or a
  separate audit service).
- **Causal completeness.** Every state-changing API call writes one or
  more audit events before responding success. Failed attempts that
  reveal authentication state (logins, signature attempts) are also
  audited.
- **Captured fields, minimum.** Event id; UTC timestamp from a trusted
  clock; acting user id; target entity type and id; action verb;
  before-value and after-value (or a hash plus a separately stored
  delta); reason text where the workflow requires one; client context
  (IP or trusted-tunnel id).
- **Tamper evidence.** Periodically hash-chain audit batches and store
  the chain head externally (an internal log service or a trusted
  timestamp). Without this, "append-only" is a promise, not a property.
- **Readable surface.** Provide a per-record audit view scientists can
  read without filing a ticket. Hidden audit logs erode trust.

### 5. Model permissions and team boundaries

Avoid ad-hoc booleans. Pick a model and stick to it.

A workable default:

- **Roles within a team** — viewer, contributor, lead, administrator.
  Roles grant verbs (read, write-draft, sign, lock, administer).
- **Per-record sharing** — a record can be shared read-only or
  contribute-only with named users or other teams. Sharing is itself
  an audited event.
- **Cross-team objects** — protocols and inventory may be promoted to
  organisation-wide read with explicit owning team.
- **Signature authority** — the right to apply a *witness* or *approver*
  signature is a separate grant, not implicit in the lead role. A
  witness cannot also be the author of the record they witness; the
  system must enforce this at signature time.
- **Service accounts** — distinct identity class, cannot sign, cannot
  belong to a team-lead role.

Document the matrix of (role x verb) and the matrix of (signature kind
x who can apply it). Make the rules machine-checkable.

### 6. Plan integrations as adapters, not as core

The notebook should not embed instrument drivers or LIMS schemas.
Instead:

- Expose a small, stable **ingest API** — create attachment, create
  measurement, link to experiment, set lineage.
- Expose a small, stable **lookup API** — resolve sample by id, fetch
  protocol version, search inventory.
- Place vendor-specific code in dedicated **adapter services** that
  consume those APIs. Adapters fail loudly and do not write directly to
  the experiment body.
- For identity, integrate with the institutional identity provider
  (SAML or OIDC) rather than maintaining a separate password store.
  Local accounts remain for break-glass administrators only.

A separate skill in this niche covers instrument integration in depth.

### 7. Plan storage, backup, and archival

- **Attachments** are content-addressed (sha-256) and stored in object
  storage. The database stores the hash, name, mime type, size, and
  pointer; never the bytes inline.
- **Cold archive** — locked records older than a retention threshold
  move to write-once cold storage with their audit chain.
- **Retention horizon** — choose a default (commonly ten years, longer
  for clinical-supporting data) and make per-record extensions
  explicit. Never let retention be "indefinite by accident".
- **Restore drills** — at least annually, restore a sample of records
  from cold storage into a parallel environment and verify hashes.
  Untested backups are not backups.

### 8. Stage the readiness ladder

Make the regulatory trajectory explicit as a ladder, not a switch:

1. **Research deployment.** All architectural primitives present
   (immutability after lock, audit trail, signed records), but the
   policy environment is light. Used for non-regulated science.
2. **GLP-aligned deployment.** Procedural controls added: training
   records, periodic audit-trail reviews, validated backup-restore,
   change-control board for system changes.
3. **21 CFR Part 11 ready.** Full electronic-signature semantics, user
   identity bindings, validated state, controlled documentation, and a
   gap analysis on record. A dedicated skill in this niche covers the
   Part 11 readiness assessment.

Build the architecture so movement up the ladder is configuration and
policy, not a rewrite.

## Inputs

- An honest description of the organisation, including the regulatory
  trajectory and the lab's current pain points.
- A list of the systems the notebook must talk to (identity providers,
  instruments, inventory, analysis pipelines).
- A statement of constraints (self-hosted vs. cloud, in-house engineers
  available, budget posture).

## Outputs

A markdown architecture brief containing:

1. Operating context and open questions.
2. Entity model with diagram description and per-entity field lists.
3. Record lifecycle and amendment policy.
4. Audit-trail design and tamper-evidence approach.
5. Permission model and signature-authority matrix.
6. Integration surface (ingest API, lookup API, adapter pattern).
7. Storage, backup, archival, and retention plan.
8. Regulatory readiness ladder with the deployment's current rung.
9. A short risk register flagging the top architectural risks.

## Examples

**Prompt.** "Eighty-person biotech, mostly antibody discovery, three
teams, currently on shared drives. Want a notebook within nine months.
Regulated work is two years out."

**Expected output shape.** Entity model anchored on Experiment with
strong Sample and Protocol entities; project layer recommended because
of multi-team antibody campaigns; locking via author-submit plus
witness-sign; addendum-style amendments; audit trail with daily
hash-chain to internal log service; SAML to corporate identity
provider; object storage for attachments with sha-256 addressing;
research-tier rung today, GLP-aligned rung targeted before any
regulated programme starts; risk register flags the witness-signature
training gap and the absence of validated restore drills.

## Limitations

- This skill does not select between named ELN products. Product
  comparisons depend on procurement and integration constraints that
  are out of scope.
- It does not produce database schemas or API specifications. Those are
  downstream engineering artefacts.
- It does not certify any deployment as regulation-compliant.
  Regulatory readiness requires a qualified review.
- The audit-trail and signature guidance is conservative by design.
  Specific industries (analytical services labs under ISO 17025, GxP
  contract organisations) layer additional requirements that must be
  consulted separately.

## Sources reviewed

Methodology informed by a survey of widely deployed open-source ELN
systems and public regulatory guidance. No prose, code, or schema was
copied; the systems below were read to triangulate the common
architectural shape of the field.

- eLabFTW project repository (AGPL-3) — multi-team self-hosted ELN with
  trusted-timestamping and audit features.
- SciNote ELN repository (MPL-2.0) — life-science notebook with
  project/experiment/task/protocol hierarchy.
- Chemotion ELN repository (AGPL-3) — chemistry-focused notebook with
  reactions, samples, wellplates, and analyses as first-class entities.
- RSpace open-source platform repository (AGPL-3) — notebook plus
  inventory with auditability emphasis.
- Indigo ELN v2 repository (MIT) — chemistry notebook with a separate
  signature module and chemical-registration service.
- US 21 CFR Part 11 (eCFR) and FDA Part 11 scope-and-application
  guidance — public regulation, used for the readiness-ladder framing.
