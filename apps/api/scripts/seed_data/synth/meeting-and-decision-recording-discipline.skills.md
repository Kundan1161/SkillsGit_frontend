---
id: skillsgit-curated/meeting-and-decision-recording-discipline
version: 1.0.0
name: Meeting and Decision Recording Discipline Designer
description: Designs a durable practice for recording meetings and decisions in a versioned knowledge base — Decision Record template, async-first contribution, propagation to the handbook, archival rules, and link-back from related material.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:handbook-as-code, decision-records, async-collaboration, knowledge-management, meeting-notes, documentation, governance, transparency]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - decision record
  - meeting notes
  - ADR
  - decision log
  - async decision making
  - meeting documentation
  - decision making process
  - knowledge capture
  - meeting hygiene
  - decision archive
  - rationale documentation
  - record decisions
example_invocations:
  - "Our team makes decisions in Slack and then nobody remembers why. Design a decision-recording discipline."
  - "We want to adopt ADRs beyond engineering — for operational and product decisions too. Propose the template and the workflow."
  - "Design how meeting notes flow from a call into our handbook so decisions don't get lost."
inputs:
  - name: team_context
    type: text
    required: true
    description: Team size, distribution (co-located, hybrid, async-remote), and the kinds of decisions made — technical, organizational, product, commercial.
  - name: current_practice
    type: text
    required: false
    description: How decisions and meetings are recorded today, if at all — note-taking tools, meeting culture, whether ADRs or RFCs exist in any form.
  - name: pain_points
    type: text
    required: false
    description: Specific failures the team has experienced — repeat litigation of settled questions, surprise about why a thing exists, new joiners unable to understand past trade-offs.
  - name: handbook_state
    type: choice
    required: false
    description: Whether the team has a handbook system to propagate decisions into. If none, the skill designs the practice as a standalone artifact stream.
    choices: [none, exists-immature, exists-mature]
outputs:
  - name: decision_recording_methodology
    type: markdown
    description: A complete methodology document — when to record, the Decision Record template, the meeting-notes-to-record workflow, async review process, archival policy, link-back rules.
  - name: decision_record_template
    type: markdown
    description: A reusable Decision Record template, ready to drop into a repository.
  - name: meeting_notes_template
    type: markdown
    description: A meeting-notes template that includes the structured fields needed to harvest decisions later.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a team has noticed that the same arguments keep happening — every six months someone proposes the change that was rejected last year, with no shared memory of why it was rejected and what evidence would now justify revisiting it. The skill is also appropriate when a team is going async or scaling beyond the size where everyone can plausibly remember every meeting, and when new joiners routinely ask "why do we do it this way?" with no good place to point them. The forcing event is usually a specific moment of regret: a decision was made, the meeting ended, no record was kept, and three months later the team is paying the cost of having to re-derive the rationale.

The skill produces a discipline, not a tool selection. The discipline names which decisions are worth recording (not all of them), what a record contains, how a meeting is shaped to produce a record, how the record is reviewed asynchronously, where it lives, how it is found later, and how it propagates into longer-lived handbook content when its conclusions stabilize. The discipline is opinionated; teams that adopt it gain the ability to refer back, to onboard new joiners faster, and to revisit decisions on evidence rather than energy. Teams that find the discipline burdensome typically have a misalignment about whether decisions are worth recording — that misalignment, not the template, is the real issue.

The skill is not the right tool when a team operates entirely in real time with stable membership and a high oral-tradition tolerance (rare, and usually a state that ends when the team grows or someone leaves); when the decisions in question are entirely tactical and consequence-free; or when the team has a heavily regulated decision-tracking process already (the skill's discipline is lighter than typical compliance documentation and is not a substitute).

## How to apply

The skill follows a ten-step sequence. The order matters because the template cannot be designed before the recordable-decision criteria are set, the workflow cannot be designed without the template, and the propagation rules cannot be designed without a stable workflow.

1. **Define the recordable-decision criterion.** Not every choice is worth a record. The criterion should be sharp enough that a team member can answer in fifteen seconds whether a given choice qualifies. A useful default: record a decision if it (a) involves trade-offs the team had to weigh against alternatives, AND (b) is expected to remain in force for more than a quarter, AND (c) would be expensive or confusing to reverse without context. Choices that meet one but not all three (a one-off operational ruling, a temporary workaround, a routine prioritization within an existing framework) are not recorded. Naming the criterion explicitly is the single intervention that prevents the practice from drowning under volume in month two.

2. **Choose the Decision Record shape.** The shape has converged across the industry around a stable set of fields: title, status (proposed, accepted, superseded, deprecated), date, context, the decision itself, alternatives considered, consequences, follow-ups. Adapt these fields to the team's decision classes (technical decisions may need a "fit with existing architecture" field; product decisions may need a "user impact" field) but keep the spine stable. Records are numbered monotonically so they sort and reference cleanly, named with a short hyphenated descriptor, and committed alongside any related source — code or other artifacts — to keep the historical trail intact.

3. **Insist that records are immutable after acceptance.** A core principle: once a record reaches the accepted status, its text is frozen. Subsequent changes are made by writing a new record that supersedes the old one, with the new record naming the predecessor and the predecessor's status updated to "superseded by." This rule has two purposes. It preserves the historical accuracy of what was decided when (a record edited a year later becomes a fiction). It also creates a chain of reasoning a future reader can follow forward: when did we change our mind, and why? Teams that edit records freely lose both properties and the records degrade into a flat policy reference, which is a less useful artifact.

4. **Shape meetings so they produce decision records as a by-product, not an afterthought.** A meeting that is intended to reach a decision uses a structured agenda: state the question, state the constraints, surface alternatives, weigh them, choose, name the consequences, name the owner of each follow-up. The note-taker captures these directly into a draft record using the template rather than into free-form notes. At the end of the meeting, the draft is read back. By the time the call ends, the record is 80% written. The remaining 20% — a final read-through and asynchronous review — happens after. Meetings that fail to produce a draft record probably did not actually reach a decision; that is itself useful information.

5. **Make the asynchronous review path the default, not the exception.** Drafted records are posted for review with a stated review window — usually three to five business days. Reviewers comment in the document, raise objections, suggest amendments. The author addresses each comment explicitly. If the review window closes with no unresolved objections, the record is accepted. If objections remain, a follow-up synchronous discussion is scheduled — but only on the specific objection, not on the whole decision. This async-first model is faster than it sounds because most reviewers' comments are minor clarifications, and it produces a much higher-quality artifact than a synchronous-only model where the record is written from memory days after the meeting.

6. **Establish a stable storage location with a predictable URL pattern.** Decision records live in a single directory in the repository, with file names that include the number and the descriptor (e.g., `0042-payment-provider-selection.md`). Stable URLs matter: records will be linked from code comments, from handbook pages, from chat threads, from external systems. A URL that breaks under reorganization breaks every link to it. The directory is flat — sub-directories by team or topic introduce ambiguity about where a cross-cutting decision belongs. If volume becomes hard to navigate, an index page with topic tags solves the navigation problem without losing flat-URL stability.

7. **Define the propagation rule from decision record to handbook content.** A decision record captures the moment of decision; the handbook captures the durable convention. After a record is accepted and the decision has been in force long enough to stabilize (typically a quarter), the conclusion propagates into the relevant handbook page as a positive statement: "We use payment provider X for European transactions" rather than "On date Y we decided X over Z because of M and N." The record remains accessible via a link, but the handbook page reads cleanly without forcing the reader through the historical reasoning. This propagation is owned by the page owner; the record's "consequences" section names the page that will receive the propagation.

8. **Specify the link-back discipline rigorously.** Every handbook page whose content was shaped by a specific decision record links back to that record in a footer or sidebar. Every piece of code or operational tooling whose existence depends on a recorded decision carries a comment referencing the record number. Every onboarding path that explains "why we do it this way" points to the record for the deep version. The link-back discipline is what makes the records load-bearing rather than ornamental: a record nobody links to and nobody reads might as well not exist.

9. **Archive supersession, do not delete.** Superseded records remain in the directory with their status updated. Deprecated records (decisions whose subject matter no longer applies — a tool the team no longer uses, a process retired) remain with status updated. Nothing is removed; the records directory is an append-only archive. The historical record's value increases over time because pattern-spotting across years of decisions is one of the practice's hidden returns. A team that deletes deprecated records loses the ability to learn from its own history.

10. **Build a quarterly review of the recent record stream into the team cadence.** Once a quarter, someone — usually the operations lead or the team lead — scans the records accepted in the prior quarter, looks for patterns (decisions clustered around the same axis, decisions that quietly contradict each other, decisions whose stated consequences did not materialize), and circulates a short summary. This review is the closing of a feedback loop. It surfaces emerging principles that may deserve their own handbook section, surfaces drift, and demonstrates to the team that records are read after they are written, which sustains the discipline.

### Decision record template (canonical form the skill produces)

The template the skill outputs has this structure. Field names are exact; the template is meant to be filled in without modification.

```markdown
# DR-NNNN: <short descriptor>

**Status:** Proposed | Accepted | Superseded by DR-XXXX | Deprecated
**Date:** YYYY-MM-DD
**Decision class:** technical | product | organizational | commercial | other
**Owner:** <role, not a person>

## Context

Two to four paragraphs answering: what question are we trying to answer, why now, what constraints apply, who has a stake in the answer. The reader of this section three years from now should be able to reconstruct the situation without external context.

## Decision

A single declarative paragraph stating what we are doing. Active voice, present tense. "We use X." Not "We will consider using X."

## Alternatives considered

For each serious alternative: a paragraph describing it, why it was considered, and why it was not selected. Two to four alternatives are typical; one is suspicious (it suggests the decision was foregone), and five-plus suggests the question was framed too broadly to decide.

## Consequences

What we now have to do, build, change, or accept because of this decision. This section should also name the handbook page(s) that will be updated as a result, and any follow-up records expected.

## Follow-ups

A numbered list of concrete actions, each with an owner and a target date. These are the items that turn the record into a forcing function for change rather than an inert document.
```

### Meeting notes template (shaped to harvest decisions)

```markdown
# <meeting title> — YYYY-MM-DD

**Attendees:** <names>
**Recorder:** <name>
**Decisions targeted today:** <one-line per decision, or "none"; meetings without targeted decisions are fine, they just produce a different artifact>

## Agenda

1. <item>
2. <item>

## Discussion notes

<free-form running notes, captured in flight>

## Decisions reached

For each decision reached, a draft record block (the template above, lightly filled). These draft blocks are extracted after the meeting into the records directory.

## Action items

<table of action, owner, due date>

## Open questions carried forward

<unresolved items that did not become decisions today>
```

### Anti-patterns the methodology calls out

- **The over-record trap.** The team records every choice, including trivial ones. Within a month the records directory has 200 entries, half of which are tactical, and nobody reads any of them. Fix: re-apply the recordable-decision criterion ruthlessly; archive the trivial ones with a one-time bulk sweep.
- **The edit-the-record trap.** A team edits an accepted record when the decision changes, on the reasoning that "we keep the records up to date." Within a year the records are a flat policy file and the historical reasoning is lost. Fix: the immutability rule is non-negotiable; supersede with a new record.
- **The orphan record trap.** Records exist but nothing links to them. Future readers never find them. Fix: the link-back discipline; a record with zero inbound links after its propagation date is a discoverability bug to be fixed.
- **The retroactive-record trap.** Records are written days or weeks after the meeting, from memory. Quality degrades dramatically. Fix: the draft is written during the meeting; if no draft emerged, no decision actually was reached and the meeting needs a follow-up.
- **The performance-record trap.** Records are written to look impressive to outsiders rather than to be useful to insiders. They become press releases. Fix: records are not external documents; the audience is the team and its successors, and the voice should reflect that.
- **The single-author trap.** One conscientious team member writes most of the records; everyone else free-rides on their discipline. When that person leaves or burns out, the practice collapses. Fix: the recorder role rotates by meeting; participation in record drafting is a normal team expectation, not a specialist role.
- **The status-stuck-on-proposed trap.** Records accumulate in proposed status because no one closes the review window or marks them accepted. The directory fills with semi-decisions. Fix: every proposed record has an explicit review-window expiry date in its frontmatter; the steward sweeps weekly for expired proposals and forces them to accepted or withdrawn.
- **The hidden-amendment trap.** A team adds clarifications to an accepted record as "minor edits" — fixing a typo, then later a clarifying phrase, then later a small substantive correction. The record drifts from its accepted version. Fix: any change to the substantive content of an accepted record (anything beyond strict typo correction) requires a superseding record; the rule is enforced by review.

### Decision classes and how the template flexes

The base template suits any decision worth recording, but four decision classes recur and benefit from minor template adjustments. The skill names these so teams do not feel they have to choose between a one-size-fits-all template and inventing their own.

- **Technical decisions** add an "implementation status" field tracking whether the decision has been put into code, partially implemented, or remains theoretical. Technical alternatives sections typically list more options because the design space is richer.
- **Product decisions** add a "user impact" field describing the experience implication. The context section is heavier because product decisions are downstream of customer research that needs summarizing.
- **Organizational decisions** (team structure, reporting lines, role definitions) add a "people affected" field that names the roles or teams. The consequences section is heavier because organizational changes ripple further than they appear.
- **Commercial decisions** (vendor selection, pricing changes, partnership terms) add a "review trigger" field stating the condition under which the decision should be re-examined — typically a contract renewal date or a quantified change in usage. Commercial decisions are uniquely time-bound and benefit from prepaid reconsideration.

### The role of the steward

The discipline benefits from a named steward. The steward's job is not to write records (that is the team's job); it is to maintain the practice's hygiene. The steward responsibilities:

- Sweep the records directory weekly for stuck-on-proposed entries and expired review windows.
- Run the quarterly retrospective summarizing the prior quarter's record stream.
- Coach new joiners on the practice in their first month, including walking through three to five recent records as examples.
- Hold the line on immutability when contributors propose to edit accepted records.
- Maintain the directory's index and tag system so records remain findable as volume grows.

The steward role can be part-time and rotates well — a six-month rotation is a reasonable cadence, and the handoff itself becomes an opportunity to re-examine the practice.

## Inputs

- **Team context (required, text).** Team size, distribution model, and decision classes. Calibrates record granularity and review cadence.
- **Current practice (optional, text).** Existing practices ground the recommendation; without it, the skill produces a more generic methodology.
- **Pain points (optional, text).** Specific failures the team has experienced. The skill ties the discipline's design choices back to the named pain points so the recommendation is recognizably aimed at the team's problems.
- **Handbook state (optional, choice).** Drives whether the propagation rule is fully designed (mature handbook) or sketched as a future state (no handbook).

## Outputs

A methodology document with the full sequence above; a clean Decision Record template; a meeting notes template that is shaped to harvest decisions into records.

## Examples

### Worked example: a thirty-person product team migrating from chat-based decisions

**Input team context:** "Thirty people, two-thirds remote, mix of product, design, and engineering. Decisions span technical (architecture), product (which features to build), and organizational (how teams are structured)."

**Input current practice:** "Decisions happen in Slack threads or on video calls. Sometimes someone summarizes in a thread; the summary is usually a paragraph. There's an engineering ADR repository but it has nine entries and last received a commit four months ago."

**Input pain points:** "Two months ago we relitigated a build-versus-buy decision we'd settled in the spring. Nobody could find the original reasoning. Last month a new engineer asked why we use Postgres and the only answer was 'because we always have' — which is not true; there was a decision, but it isn't written down."

**Input handbook state:** "exists-immature" — pages exist but ownership is spotty.

**Expected output (excerpt):**

> ## Recordable-decision criterion (your team's variant)
>
> Record a decision when all three apply:
>
> 1. The decision involved choosing among alternatives the team weighed seriously. Routine prioritization within an existing framework — choosing which two of four features to ship this quarter under a settled roadmap — does not qualify. Choosing between Postgres and a managed key-value store does.
> 2. The decision is expected to remain in force for at least a quarter. A two-week workaround is not recorded. A tool selection, a process change, a structural change to how a team is organized, is.
> 3. Reversing or revisiting the decision later would require significant context to understand why the original was made. The Postgres-or-key-value example qualifies. "We're going to standardize on this Slack channel naming convention" probably does not, unless the team's structure makes it harder than it sounds.
>
> Default: when in doubt, record. The cost of recording is small; the cost of not recording is paid later by the team member who has to re-derive the reasoning.
>
> ## Workflow tuned to your team
>
> Each decision meeting produces a draft record by end-of-meeting using the meeting-notes template. The recorder is named at the start of the meeting and rotates — recording is a team responsibility, not a designated-scribe role.
>
> Draft records are posted to a `#decision-review` channel and pinned to the records directory with status "Proposed." The review window is three business days, sized for your time-zone spread. Reviewers comment in the document; the author resolves each comment. Records with no remaining objections at the end of the window are merged with status "Accepted." Records with unresolved objections trigger a 30-minute synchronous discussion focused only on the open objection.
>
> Propagation: each accepted record's "Consequences" section names the handbook page(s) to update and the owner who will update them, with a 30-day target. The page edits link back to the record.

### Worked example: a fifteen-person operations team standardizing decisions in a regulated industry

**Input team context:** "Fifteen people, mostly co-located but with three remote contractors. Operations team inside a regulated financial-services firm. Decisions span tool selection, process changes, and vendor relationships."

**Input current practice:** "Decisions usually happen in weekly leadership meetings. Notes are taken in Confluence under date-stamped pages but they're free-form. Audit trails are required for any decision involving customer-impacting processes."

**Input pain points:** "Auditors have flagged that decision rationale is hard to reconstruct from our meeting notes. Internally, we keep revisiting vendor decisions because the original reasoning isn't surfaceable."

**Input handbook state:** "exists-mature"

**Expected output (excerpt):**

> ## Decision recording, calibrated for your audit context
>
> Your discipline does double duty: internal clarity and external auditability. The design adjustments:
>
> 1. Decision class is captured explicitly in frontmatter (technical, process, vendor, customer-impacting). Customer-impacting decisions are tagged for the audit-evidence pipeline.
> 2. Every record names the accountable executive owner (the person whose role would be questioned in an audit), separately from the page owner who maintains the record. For non-audit-relevant decisions, these are usually the same person; for audit-relevant decisions, the accountable owner is typically a director or above.
> 3. The supersession chain is strictly maintained because audit reconstruction depends on the chain remaining intact. The steward role includes monthly integrity checks (every record's supersession links resolve correctly, every "superseded by" pointer is bidirectional).
> 4. The records directory is included in the audit-evidence scope for the firm's annual review; the directory's structure and contents are surfaced to auditors as part of the standard package, alongside other operational records.
>
> Beyond these adjustments, the practice is the standard one. Customer-impacting decisions get the most rigorous treatment, but routine decisions still benefit from the lightweight discipline.

## Adoption arc — what the first six months look like

Teams adopting this discipline pass through recognizable stages. The skill names them so the team can anticipate and not interpret early friction as failure.

**Weeks one and two: introduction and overhead.** The discipline is announced, the template is shared, the first one or two records are drafted in meetings. Contributors find the new structure clunky; the meetings run five minutes longer because of the read-back. The first records are over-long because contributors are unsure what level of detail is right. This is expected. The steward keeps a light hand and lets the practice settle.

**Weeks three through six: format calibration.** Teams converge on the right length for records (typically one to two pages), the right level of alternative-detail (two to three serious alternatives, not exhaustive enumeration), and the right voice (informative, not legalistic). The first records get superseded as the team's thinking sharpens; this is healthy and demonstrates the supersession mechanic.

**Weeks seven through twelve: integration with the handbook.** The first propagations into handbook pages happen. Page owners begin to expect that contentious changes are accompanied by a decision record. Cross-links from handbook pages to records become routine. New joiners notice the records and use them; the practice begins to look like part of the team's identity.

**Months three through six: maturity and selectivity.** The team's instinct for what is recordable becomes tacit. Volume stabilizes, typically around one to three records per week for a thirty-person team. The quarterly retrospective produces its first useful pattern observations. Some teams discover they have been over-recording in one area and under-recording in another; the discipline self-corrects.

Teams that drop the practice usually drop in weeks two through four, when the cost is visible and the benefit has not yet accumulated. Sustained sponsorship from the team lead through this period is the strongest predictor of adoption.

## Decision records as an onboarding tool

A side benefit worth naming explicitly: the records directory is one of the most powerful onboarding artifacts a team has. A new joiner reading thirty representative records gets a faster education on the team's reasoning style, technical taste, organizational dynamics, and ongoing concerns than weeks of meetings would provide. The handbook section on onboarding should reserve a half-day in the new joiner's first month for reading recent records selected by the manager. Records produced with this future reader in mind are recognizably different from records produced for an audit — they explain rather than catalog, they show reasoning rather than conclusions only, they reveal the team's character. The discipline benefits when contributors are aware that their records will be read by someone who was not in the room.

## Decision records and AI assistants

Teams working with AI assistants find that decision records have additional value as context the assistant can be pointed to. When the assistant is asked a question whose answer was decided in a record ("why do we use this tool rather than that one?"), surfacing the relevant record is a higher-quality answer than re-deriving the reasoning from scratch. The records directory becomes part of the team's institutional context that the assistant draws on. This is worth surfacing in the propagation step: a well-tagged records directory is a load-bearing asset for AI-augmented team work, not just for human readers.

## Common questions teams ask when adopting the discipline

- **"What about decisions made in chat threads?"** Chat is where many decisions actually happen, particularly in async-first teams. The discipline accommodates this: a thread that reaches a decision should be summarized into a draft record by whoever called the conclusion, then run through the standard review window. The thread is not the record; the record is what was distilled from it.
- **"How long should a record be?"** Most records are one to two pages. Records under half a page typically under-explain the alternatives or the consequences; records over four pages usually try to make multiple decisions at once and should be split. The exception is decisions with rich technical or commercial context — those can earn additional length, but length should be in service of clarity, not thoroughness for its own sake.
- **"Who reads these records?"** A small fraction are read intensively at the time of acceptance (reviewers); a larger fraction are read occasionally as referenced from handbook pages or other records; the rest are read rarely but are searched when someone asks "did we decide on this?" The discipline is calibrated for the searched-when-needed reader; that reader's experience is the test of the practice.
- **"Should records be public?"** Internal-only is the default. Some teams find that publishing a curated subset of records externally builds hiring and trust signal; this is optional and benefits from the same private-public split the handbook architecture uses.
- **"What about decisions that turn out to be wrong?"** Bad decisions remain in the record, superseded by the correcting record. The chain shows learning over time. Hiding bad decisions damages the records' value as a historical artifact; the discipline depends on records being honest rather than self-flattering.

## What the practice looks like steady-state

A team that has run the practice for a year produces decision records with the following characteristics:

- Records are recognized by length and tone within the first paragraph; voice is consistent across the team because the template's structure carries it.
- Roughly 70% of records are accepted within their review window without contention; roughly 25% accumulate substantive review comments and are amended before acceptance; roughly 5% are withdrawn after review surfaces a problem with the underlying decision.
- About one in twenty records gets superseded within two years; another one in ten gets deprecated as its subject matter retires. The rest remain accepted and live indefinitely.
- New joiners cite records as one of the most useful onboarding artifacts; the practice has effectively become a documented intellectual history of the team.
- Repeat-litigation incidents (the same decision relitigated months apart) have dropped meaningfully from the pre-practice baseline.

## Limitations

- The skill produces the discipline, not the muscle. Discipline takes a quarter of consistent practice before it becomes automatic; the first month is the hardest, and many teams abandon during it. The skill flags this risk but cannot mitigate it; a sponsoring lead who reinforces the practice through the first quarter is essential.
- The skill's methodology assumes a baseline level of trust within the team. Records expose reasoning, including reasoning that turned out to be wrong. In low-trust environments contributors hedge their records into uselessness, or the records become political. The skill cannot solve trust deficits; teams in that situation should address the underlying dynamic before adopting the discipline.
- The skill does not select tools. The discipline runs on plain Markdown and Git, but it can be implemented on top of structured wiki tools, dedicated ADR-management tools, or hosted documentation platforms. Tool choice has secondary effects on adoption (a tool the team already uses lowers friction) that the skill does not optimize for.
- The skill's quarterly review depends on someone owning it. If that ownership is unassigned, the review lapses and the closing-the-loop benefit is lost. Name the reviewer at adoption time.
- The skill does not address heavily regulated decision processes (medical device design history files, financial-services change-control records). Those have specific format and retention requirements outside this skill's scope.

## Sources reviewed

Sources informed the methodology only — no prose was copied. License tags below.

- https://adr.github.io/ — methodology page on architectural decision records; informational, no explicit license on the methodology principles
- https://github.com/joelparkerhenderson/architecture-decision-record — MIT licensed (examples and templates for ADRs)
- https://martinfowler.com/bliki/ArchitectureDecisionRecord.html — article by Martin Fowler; copyrighted commentary, used to inform methodology only (no prose reproduced)
- AWS Prescriptive Guidance on ADR process (https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/) — proprietary documentation, used to confirm the convergence of the ADR pattern in industry practice (no prose reproduced)
- Generic transparent-company handbook practices on meeting and decision recording (CC-BY-SA-licensed reference material was reviewed; no prose, structure, or trademarked names were carried into this skill — methodology only).
