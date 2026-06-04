---
id: skillsgit-curated/handbook-system-architect
version: 1.0.0
name: Company Handbook-as-Code System Architect
description: Designs a public-or-internal company handbook system kept in source control — information architecture by reader, single-source-of-truth principle, page ownership, contribution workflow, freshness audits, and link discipline.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: operations
tags: [niche:handbook-as-code, knowledge-management, documentation, remote-work, single-source-of-truth, governance, onboarding, transparency]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - company handbook
  - handbook as code
  - employee handbook
  - team wiki
  - knowledge base architecture
  - single source of truth
  - documentation strategy
  - public handbook
  - remote-first documentation
  - internal docs
  - team handbook
  - org wiki
example_invocations:
  - "We're a 60-person remote-first company and our docs are scattered across Notion, Drive, and Slack. Design a handbook system we can stand up in 90 days."
  - "Propose an information architecture for a public-facing handbook for our 200-person consultancy."
  - "Our wiki is a graveyard. Architect a replacement built on Markdown in Git with clear ownership."
inputs:
  - name: company_context
    type: text
    required: true
    description: Headcount, lifecycle stage, remote or hybrid posture, industry, and any constraints (regulated industry, confidentiality requirements, multi-language needs).
  - name: current_state
    type: text
    required: false
    description: Where knowledge lives today — wiki tools, shared drives, chat-pinned messages, tribal knowledge. Pain points the team has named.
  - name: audience_scope
    type: choice
    required: false
    description: Who the handbook serves. Public means external readers (candidates, customers, the broader community) read it too.
    choices: [internal-only, internal-and-candidates, fully-public]
  - name: technical_tolerance
    type: choice
    required: false
    description: How comfortable contributors are with Git, Markdown, and pull-request workflows. Affects the contribution model that can be sustained.
    choices: [low, mixed, high]
  - name: constraints
    type: text
    required: false
    description: Legal, compliance, or trade-secret constraints that bound what can be shared, even internally.
outputs:
  - name: handbook_architecture
    type: markdown
    description: A complete architecture document covering structure, ownership model, contribution workflow, freshness policy, link discipline, and an implementation roadmap with milestones.
  - name: top_level_map
    type: markdown
    description: A standalone top-level information map (the table of contents and reader-paths) that can be circulated separately for stakeholder review.
  - name: governance_charter
    type: markdown
    description: A short governance charter naming the steward role, the editor pool, the contribution workflow, the merge policy, and the freshness audit cadence.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Use this skill when a company is moving its operational knowledge out of fragmented places — chat threads, drive folders, wiki software where every page has different conventions, the institutional memory of three long-tenured employees — and into a deliberately designed handbook held in version control. The trigger is usually a forcing event: rapid hiring outpacing oral tradition, a remote or hybrid transition that ended the office-by-osmosis model, a leadership change exposing how much hangs on one person's head, or a transparency commitment requiring a public-facing handbook.

The skill is appropriate when the team has accepted three premises. First, that documentation will be treated as a primary work product, not the cleanup task after the real work. Second, that a single source of truth is worth the discipline cost — having two pages on the same topic is worse than having one imperfect page. Third, that pages need owners; an ownerless handbook decays predictably within a year. If any of those three premises are not held by the sponsoring leadership, the skill should produce a smaller-scope plan (a critical-paths-only handbook) rather than a full system, because attempting the full thing without the premises produces a second graveyard.

The skill is not the right tool for a personal note system, a customer-facing product documentation site (those have specialized concerns — search-engine optimization, versioned API surfaces, multi-product navigation — outside this skill's scope), a regulatory submission dossier, or a marketing site dressed up as a handbook. It also stops short of training-content design; the handbook anchors training but is not itself a curriculum.

## How to apply

The skill walks through twelve design decisions in order. The order matters: the architecture cannot be sound until the reader map is named, ownership cannot be assigned without the architecture, and freshness policy is meaningless without ownership. Skipping forward produces handbooks that look reasonable in a screenshot but fall apart under year-two contact with reality.

1. **Name the readers in concrete categories, before naming any sections.** A handbook is structured by who reads it, not by which department wrote it. Distinguish at least: new hires in their first ninety days; current employees looking up a policy they vaguely remember; managers running a recurring process; candidates evaluating whether to apply; external partners or customers (if the handbook is public); leadership making a decision that needs precedent. For each reader, write one sentence describing the most common question they arrive with. These sentences become the seed for the top-level map. If a reader cannot finish their question in one sentence, split them into two readers.

2. **Decide the single-source-of-truth boundary with brutal explicitness.** For every topic the handbook will cover, name where that topic lives if not in the handbook. Compensation philosophy lives in the handbook; the live salary spreadsheet does not. Engineering values live in the handbook; the codebase-specific style guide may live next to the code. The HR system holds the source of truth for who-reports-to-whom; the handbook reflects rather than duplicates it. Write the boundary as a list of pairs: topic → canonical home. Any page that violates the boundary becomes a candidate for deletion or for being demoted to a stub-with-link.

3. **Choose the structural backbone before populating it.** Three structural backbones recur in practice. Reader-path backbone (sections named for who reads them: "For new joiners," "For managers"). Lifecycle backbone (sections named for company processes: "Hiring," "Onboarding," "Performance," "Off-boarding"). Topic backbone (sections named for substantive areas: "Engineering," "People," "Finance"). Pick one as primary and use the others as cross-cutting indexes, not parallel structures. Mixing backbones at the top level is the most common information-architecture failure: it creates places where the same content plausibly belongs in two top-level sections, which guarantees duplication.

4. **Limit top-level sections to seven, and depth to three.** A reader who has to traverse four levels to find a policy will give up; a reader who sees twelve top-level sections cannot scan. Seven is approximate but a useful ceiling. Three levels of depth — top section, sub-area, page — covers almost every real handbook. If a fourth level seems necessary, it usually indicates that a sub-area is actually a separate handbook (engineering wiki, design system documentation) that should live elsewhere with a link from the handbook rather than nested inside it.

5. **Specify the per-page contract: every page has one job, one owner, and one freshness date.** A handbook page is not a free-form document. The page contract requires a top-line statement of what the page is for, an owner field (a named role, not a person — "Head of People," "Engineering Manager for Platform"), a last-reviewed date, and a body that addresses one question. Pages that try to be reference, narrative, and policy at once become unusable; split them. The owner field is the single most important architectural decision, and it must point to a role that survives turnover. "Maintained by Maria" rots when Maria leaves; "Maintained by the People Operations team" persists.

6. **Define the contribution workflow with a default merge path and an exception path.** The default path is the contribution model the system is designed for — typically: open a pull request, request review from the page owner, merge on owner approval. Most edits should take this path with low friction. The exception path is for changes that need broader signoff: anything affecting compensation, anything legal, anything externally facing that needs a brand or comms check. Name the exception classes explicitly; if the exception classes are unnamed, every contributor will route everything through the exception path "to be safe," and the default path will atrophy.

7. **Decide the contribution surface that matches the team's technical tolerance.** A pure Git-and-Markdown workflow is the cleanest model but excludes contributors who cannot operate it. Three pragmatic options: pure Git (high friction, strong consistency, suited to engineering-heavy companies); Git with a web editor overlay (the Git repository remains the source of truth, but contributors edit through a browser interface that opens pull requests on their behalf); Git plus a sanctioned import path from a non-Git tool (a designated Google Doc or wiki page is the staging area, and a known person periodically lifts approved content into the repository). Pick one; mixing them produces ambiguity about which copy is canonical.

8. **Establish link discipline as an architectural rule, not a style preference.** Every cross-reference between handbook pages should be a relative link that survives reorganization. Every link to an external document (a tool, a recorded video, an internal system) should carry a one-sentence description of what it points to, so a reader can decide whether to follow it. Broken links are the leading indicator of handbook rot; the architecture should include a CI check that flags broken internal links on every pull request, and a quarterly external-link audit.

9. **Build the freshness audit into the calendar from day one.** Each page's owner is responsible for reviewing it on a stated cadence — annually for most pages, quarterly for fast-changing operational pages, on-trigger for pages tied to specific systems (when the system changes, the page is reviewed). Build a dashboard that lists pages by days-since-review per owner, and route a monthly digest to each owner with their stale pages. The freshness audit is the single mechanism that prevents the handbook from becoming a museum.

10. **Plan the public-versus-internal split explicitly if the handbook will be public.** Decide at the architecture level which sections are public-by-default and which are private-by-default. Private-by-default sections should still live in the same repository if possible, gated by access rather than scattered into a separate system; the cost of maintaining two systems exceeds the cost of an access boundary. Compensation specifics, customer names, security incident detail, and unsigned-deal information typically remain private. Most other content can be public if the company chooses; making it public raises the contribution quality bar because external readers see drafts.

11. **Anchor onboarding to specific handbook entry points.** A handbook only becomes load-bearing if new joiners are routed to it on day one and on every subsequent question. Specify the onboarding path through the handbook: which pages every new joiner reads in week one, which pages their manager assigns role-specifically, which pages function as ongoing references. The architecture should account for this; an onboarding sub-section with stable URLs that the welcome email and the first-week schedule can link to is materially better than relying on managers to remember the relevant pages.

12. **Write the implementation roadmap as a sequenced migration, not a big bang.** Existing knowledge migrates over months, not in a sprint. Sequence the migration by reader value: first the pages a new joiner needs in week one, then the pages a manager runs processes against, then policies, then narrative content. For each migration batch, name the source, the page owner, and the deletion date for the original (the migration is incomplete until the original is removed; otherwise both copies persist and the single source of truth fails by design). A 90-day initial milestone covering onboarding-essential pages is a realistic target for a 50-200 person company; full coverage takes longer.

### Pitfalls to call out explicitly in the architecture document

- **The two-source trap.** A team migrates content into the new handbook but does not retire the old wiki, so both persist. Within six months readers cannot tell which is canonical, the new handbook stops being trusted, and the team reverts. Prevention: deletion of the source is part of the migration definition of done.
- **The owner-by-default trap.** Pages are merged without an explicit owner; review falls to "whoever last edited it," which decays to nobody. Prevention: the validator on merge requires the owner field be set to a known role.
- **The everything-in-the-handbook trap.** The handbook expands to swallow project documentation, meeting notes, customer call summaries. Within a year it has 4,000 pages and no shape. Prevention: a stated scope at the top level, and an explicit no-go list (we do not put project docs here, we do not put customer-specific notes here, we do not put draft thinking here).
- **The brand-voice trap.** External-facing pages get rewritten by marketing into press-release voice, internal contributors stop recognizing the handbook as theirs, contributions slow. Prevention: keep voice editorial guidance lightweight; the handbook's tone should be that of a colleague explaining something, not a brochure.
- **The page-as-deck trap.** Contributors arrive from a slide-deck culture and build handbook pages as slide-sequences — heavy on bullets, light on prose. The pages skim well but cannot survive without their author present to narrate them. Prevention: composition guidance encouraging full sentences for any non-checklist content, and a review heuristic that asks whether a stranger could act on the page without further explanation.
- **The version-drift trap.** A page describes a tool's behavior accurately at the time of writing; the tool updates; the page does not. Within a year half of the screenshots are wrong. Prevention: tool-tied pages carry an explicit "current as of [tool version]" stamp, and the freshness audit is triggered by tool-version changes rather than calendar alone.
- **The orphan-section trap.** A section is created for a team or function that subsequently dissolves or restructures. The section sits there with old pages, no owner, no readers. Prevention: when teams restructure, the handbook restructure is in scope of the team change; the team lead leaving is the trigger for ownership reassignment within thirty days.

### How the architecture changes with scale

The methodology adapts at three rough scale thresholds. The skill calibrates against these explicitly.

- **Under 50 people.** A single steward role can carry the whole handbook practice. Page-owner is often the function lead. Migration is fast; the entire handbook can be assembled in a quarter. The risk at this scale is over-engineering — adopting governance machinery sized for 500-person organizations. Architecture should be lean: a small section count, a flat contribution workflow with one approver per area, freshness review every six months rather than quarterly.
- **50 to 250 people.** The handbook becomes the load-bearing alternative to oral tradition. Ownership distributes across function leads with the steward as a coordinator. The migration takes two to three quarters and benefits from a phased plan. Architecture should formalize: stated SSOT boundary, an exception-path for sensitive content, freshness audits surfacing per-owner dashboards, an explicit deletion policy.
- **Over 250 people.** Multiple handbook-adjacent artifacts emerge: function-specific portals, engineering wikis, sales playbooks. The handbook's job becomes the coordinating layer that points to them rather than absorbing them. Architecture should de-emphasize containment (no, the engineering wiki does not move into the handbook) and over-invest in cross-linking and search. A dedicated handbook role (full or part-time) is usually justified at this scale.

### The governance charter — a one-page artifact

The architecture document includes a separable one-page charter that names the operating model in language a leadership group can review without reading the full architecture. The charter has six fields:

1. **Stewardship.** Who owns the handbook system overall — typically a named role (head of people operations, chief of staff, or a dedicated handbook lead at scale). The steward is not the page owner for everything; they are the owner of the architecture and the freshness practice.
2. **Editor pool.** Who can review and merge pull requests by area. Usually one to three editors per top-level section. The editor pool is updated quarterly.
3. **Default merge path.** A one-sentence statement of the standard contribution workflow.
4. **Exception classes.** The two-to-five classes of content that route through additional review.
5. **Freshness cadence.** The standing rule for how often pages are reviewed, and the trigger events that move a page's review forward.
6. **Decision authority.** Who decides when there is disagreement about a page's content, ownership, or location. Default: the page's listed owner; in conflict, the steward; in conflict with the steward, the named exec sponsor.

### Required output sections

The architecture document the skill produces follows this layout:

1. `# Handbook System Architecture`
2. `## Readers and their primary questions`
3. `## Scope and source-of-truth boundary`
4. `## Structural backbone and top-level map`
5. `## Per-page contract`
6. `## Ownership model`
7. `## Contribution workflow`
8. `## Link discipline and broken-link policy`
9. `## Freshness audit and decay-prevention`
10. `## Public-versus-internal split` (omit if internal-only)
11. `## Onboarding integration`
12. `## Implementation roadmap`
13. `## Risks and mitigation`
14. `## Appendix: governance charter`

The governance charter is a one-page summary suitable for circulation to a leadership group; the top-level map is a separate artifact that can be reviewed independently of the full document.

## Inputs

- **Company context (required, text).** Headcount, stage, remote or hybrid posture, industry, and constraints. The skill calibrates depth and formality to context — a 30-person startup gets a leaner architecture than a 500-person regulated firm.
- **Current state (optional, text).** Where knowledge lives today and the named pain points. Without this, the skill cannot anchor the migration roadmap to real content.
- **Audience scope (optional, choice).** Internal-only, internal-plus-candidates, or fully-public. Public scope raises the standards on voice, accuracy, and the private/public split.
- **Technical tolerance (optional, choice).** Determines which contribution surface the architecture recommends. Mismatch here is the most common reason handbook-as-code initiatives fail.
- **Constraints (optional, text).** Trade-secret, regulatory, or confidentiality boundaries. Drives the private-by-default categorization.

## Outputs

A complete markdown architecture document organized as above; a standalone top-level map that can be reviewed in isolation; a one-page governance charter ready to circulate.

## Examples

### Worked example: a 60-person remote-first software company moving from Notion sprawl

**Input company context:** "60 people, fully remote across six time zones, three years old, B2B software. Eighteen engineers, twelve in revenue, four in design, the rest spread across operations and people."

**Input current state:** "About 1,200 Notion pages across forty workspaces. New joiners are told 'check Notion' and get lost. Three pages on parental leave with different details. Managers maintain personal lists of links they share with their reports."

**Input audience scope:** "internal-and-candidates" — the company plans to publish some hiring-related pages externally.

**Input technical tolerance:** "mixed" — engineering and design fluent in Git, revenue and operations not.

**Expected output (excerpted from the top-level map):**

> ### Reader-path map
>
> The handbook has six top-level sections, named for the primary readers:
>
> 1. **Working here** — pages every employee needs to find: time off, expenses, benefits, IT help, office stipends. Reviewed annually; owned by People Operations.
> 2. **Joining the team** — onboarding paths, role-specific first-90-days, our hiring philosophy, what to expect in interviews. Owned by People Operations with role-specific authoring from each function head.
> 3. **How we work** — meeting norms, async communication conventions, documentation expectations, decision records process. Owned by the operations lead.
> 4. **By function** — sub-sections for engineering, design, revenue, operations, people. Each is shallow (function lead's editorial, a few cross-function process pages, links to deeper team-specific tooling). Owned by the function head.
> 5. **Company** — values, leadership, how decisions get made, the calendar of company-wide events. Owned by the CEO with editorial support.
> 6. **Public** — the subset of pages exposed externally: open roles, our hiring process, our values, our remote-work philosophy. Curated from the internal pages with a private-flag system. Owned by the head of marketing in coordination with people operations.
>
> No fourth section level is created. If a page does not fit at depth three, it indicates the section needs reshaping rather than a new level.
>
> ### Contribution model
>
> Default path: any employee opens a pull request through a web editor overlay (so non-Git-fluent contributors can edit without learning Git). The page owner reviews; the owner's approval merges. CI checks: broken-link scan, required-fields validation (owner role present, last-reviewed date present and within ninety days of the change).
>
> Exception path (changes routed for additional review):
> - compensation, benefits, or anything legal — additional approval from People Operations head and Finance.
> - external-facing copy (public pages) — additional approval from marketing.
> - values or decision-making process pages — additional approval from CEO.
>
> Exception path additions are listed at the top of the contribution workflow page; nothing else goes through exception review.

### Worked example: a 220-person consultancy publishing a fully-public handbook

**Input company context:** "220 people, hybrid (each office has roughly half-and-half in-person and remote), six offices in three countries, eight-year-old professional services firm. We want a fully public handbook as a hiring and brand asset, modeled on what the most transparent firms in our space have done."

**Input current state:** "We have a Confluence wiki, mostly internal-process focused, with around 800 active pages and an additional 1,500 archived. Our policies live in a separate document management system. Our values and how-we-work content lives on the marketing site as polished marketing copy."

**Input audience scope:** "fully-public"

**Input technical tolerance:** "mixed" — practice leads vary widely; legal and finance teams have no Git fluency.

**Input constraints:** "Client-confidential content cannot be in the public handbook. Compensation bands can be public if presented as ranges, not as individuals. Internal performance-review content stays private."

**Expected output (excerpted from the architecture document):**

> ## Scope and source-of-truth boundary
>
> The public handbook holds: our values, how we work, our hiring philosophy and process, our compensation philosophy and salary ranges by role, our policies (where publication is safe), and our editorial content describing our practice areas.
>
> The public handbook does not hold: client names or engagement details (they remain in the engagement-management system), individual compensation (HRIS only), individual performance content (HRIS only), our internal financials (controller's records), draft thinking (Google Drive working area).
>
> The internal handbook — same repository, internal access only — holds: client-engagement playbooks, internal financial summaries, sensitive HR procedures, the salary band specifics with internal context not appropriate for public framing, and the methodology for content that is not yet ready for public publication.
>
> Practice-specific deep references (legal reasoning libraries, technical pattern libraries) remain in their team-specific tools and are linked from the handbook with one-line descriptions, not duplicated.
>
> ## Public-versus-internal split
>
> Pages are tagged with `visibility: public` or `visibility: internal` in their frontmatter. The build process produces two outputs from the same repository: a public website with only public pages, and an internal website with both. The reviewer pool for any change to a public page includes a marketing-team reviewer, in addition to the page owner.
>
> Pages may transition from internal to public over time as the team gains confidence in the content. Transitions in the other direction (a public page becoming internal) are rare and require explicit steward signoff because they affect external readers who may have linked to the page.
>
> ## Ownership at this scale
>
> Top-level section owners are practice-area leads and function heads — about twelve roles. Each section owner appoints two-to-four editors with merge authority within their section. A dedicated handbook coordinator (0.6 FTE) supports the system: facilitates the freshness audits, coaches new contributors, runs the quarterly cross-section review, and maintains the link discipline checks. The handbook coordinator reports to the head of people operations.

## Choosing a structural backbone — extended guidance

The architectural decision between reader-path, lifecycle, and topic backbones is the most consequential top-level choice. The skill treats it with extended attention because mis-choosing here is hard to reverse: it cascades into ownership confusion, duplication, and search frustration that compound over years.

The reader-path backbone organizes by who reads the section. Sections might be titled "For new joiners," "For managers," "For everyone." Its strength is reader orientation — a new joiner can find their section instantly. Its weakness is overlap: a page about how to give feedback is read by both managers and individual contributors, and the backbone forces a primary placement that one of those audiences experiences as awkward. Best fit: small-to-medium companies under 200 people where reader categories are clear and overlap can be handled by cross-linking.

The lifecycle backbone organizes by company process — Hiring, Onboarding, Working, Performance, Off-boarding. Its strength is operational coherence — pages cluster naturally with the moments where they are read. Its weakness is that "Working" is a fifty-percent bucket that resists structure; the backbone often produces one tidy section and several fuzzy ones. Best fit: medium companies with mature processes where the lifecycle stages are well-defined and dominant in the team's experience.

The topic backbone organizes by substantive area — Engineering, Product, Finance, People. Its strength is owner clarity: each section has an obvious function owner. Its weakness is cross-cutting content: how-we-work pages, values, policies fit awkwardly when the rest of the structure is functional. Best fit: larger organizations where function leads own substantial portions of the handbook and the company is too big for reader-path categories to feel natural.

Hybrid backbones (mixing two approaches at the top level) almost always degrade. The exception is using one backbone primary with the others as cross-cutting indexes — a topic backbone with a "for new joiners" index that aggregates the relevant pages from across the topic sections, for instance. Cross-cutting indexes are cheap to maintain and add genuine value; structural hybrids are expensive to maintain and add confusion.

## Tool selection considerations (informational, not prescriptive)

Tool selection is out of architectural scope, but the architecture document should name what the chosen tool needs to support so the team can evaluate options without re-deriving criteria.

- **Source-control-backed storage.** Pages are stored as plain Markdown in a Git repository or equivalent. This is the load-bearing technical commitment of handbook-as-code; tools that hide content in a proprietary database make the architecture's other commitments harder.
- **Pull-request-style review workflow.** Contributions go through a review-then-merge cycle visible to everyone. Tools that lack this make the contribution workflow's discipline impossible to enforce.
- **Required-fields validation.** The owner field, last-reviewed date, and visibility tag should be enforced at merge by automated check. Tools that cannot validate these create the conditions for owner-by-default decay.
- **Stable URLs.** Page URLs should survive reorganization, or the tool should rewrite redirects automatically. Tools that break URLs on rename undermine link discipline.
- **Search that works.** Whatever the tool, search needs to be good enough that readers reach for it first. Bad search routes around the structure; readers end up asking colleagues instead of looking, and the handbook loses its load-bearing role.
- **Access control.** For internal/public splits, the tool should support per-page visibility without requiring separate systems.

Many tools satisfy these requirements: a static site generator over Git, a structured wiki tool that exports clean Markdown, even some hosted documentation platforms. The architecture's other commitments do not depend on a specific tool; they depend on the team's discipline using the tool.

## Common questions the architecture should answer pre-emptively

Stakeholders reading the architecture document will arrive with predictable questions. Pre-empting them in the document saves cycles in review and surfaces real disagreements faster.

- **"Why not just use the wiki tool we already have?"** The tool is not the issue; the discipline is. Most wiki tools could support a well-architected handbook if used with the discipline this architecture prescribes. The choice to adopt new tooling alongside this architecture is a separate decision; if the team prefers to keep the current tool and apply the discipline, the architecture supports that.
- **"How long until we see results?"** Wave-one migration (onboarding-essential pages) typically shows reader-side benefit within ninety days as new joiners route through the new content. Full coverage benefits accrue over twelve to eighteen months. The architecture is a long-horizon investment that pays compounding interest, not a one-quarter project.
- **"What if a team refuses to participate?"** Adoption is uneven, and that is acceptable in early phases. The architecture should not be held hostage to universal opt-in. Start with the function leads who are interested; reluctant teams come along as their counterparts demonstrate value, or they remain on their own systems with handbook links pointing into them.
- **"What about confidentiality?"** The public-internal split handles this for the public scenario. For purely-internal handbooks, default visibility is the team; pages requiring narrower access are gated within the same system. Confidentiality concerns rarely require entirely separate systems if access control is well-implemented.
- **"What's the cost?"** The dominant cost is contributor time, not tool licensing. A 100-person company should expect to invest roughly 0.5 to 1 FTE-equivalent in handbook work in the first year (mostly migration), tapering to perhaps 0.2 FTE-equivalent in steady state (mostly freshness audits and contributing edits as part of normal work).

## Limitations

- The skill produces an architecture, not the populated handbook. A handbook architecture is judged by what it enables; the migration that fills it is its own multi-quarter effort that depends on people, not on this document.
- The skill cannot judge whether the sponsoring leadership will sustain the discipline the architecture assumes. If leadership backs down from the single-source-of-truth principle the first time it costs them (a beloved Notion page gets nominated for deletion), the architecture cannot save itself. The skill flags this risk explicitly in the output but cannot eliminate it.
- The skill does not select tooling. Many tool choices satisfy the architecture (Git plus a static site generator, Git plus a structured wiki, even a closed-source platform that exports clean Markdown). Tooling selection has secondary considerations — search quality, access control granularity, deployment ergonomics — that the skill does not optimize for. Treat tooling selection as a downstream decision shaped by, but not determined by, the architecture.
- The skill assumes a benevolent organizational dynamic. In organizations where the handbook becomes a political artifact — pages used to litigate disputes, ownership used as territorial claim — the skill's lightweight governance fails. In that environment, more formal change control is needed and the skill's recommendations should be hardened with explicit RACI rather than role-ownership.
- The skill does not handle multi-language handbooks. Translation introduces a class of consistency problems (when the English source updates, how do the translations stay current?) that needs specialized tooling and policy. If multi-language is required, treat the resulting architecture as the single-language base and add a translation policy as an addendum.

## Sources reviewed

Sources informed the methodology only — no prose, structure, or trademarked names were copied. License tags below.

- https://github.com/madetech/handbook — license not explicit in repository README (reviewed for structural patterns only; no content reproduced)
- https://github.com/clef/handbook — CC0-1.0 (public domain dedication)
- https://github.com/hkdobrev/awesome-handbooks — CC0-1.0 (index of open-source company handbooks; used to identify the breadth of structural patterns in the niche)
- https://github.com/sourcegraph/handbook (referenced via awesome-handbooks index) — Apache-2.0
- https://adr.github.io/ — informational page on architectural decision records (referenced for the "decisions belong in version control" principle that adjacent skills extend)
- Generic references to "company handbook as code" in the niche literature (CC-BY-SA-licensed reference material was reviewed; no prose, structure, or trademarked names were carried into this skill — the niche's transparent-company patterns were abstracted as methodology only).
