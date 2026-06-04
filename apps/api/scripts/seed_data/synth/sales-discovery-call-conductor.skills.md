---
id: skillsgit-curated/discovery-call-conductor
version: 1.0.0
name: Discovery Call Conductor
description: Builds a tailored discovery agenda and question bank for a specific prospect, covering current state, desired state, gap, decision process, and success metrics — with anti-questions and objection-to-value mapping.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: sales
tags: [discovery, sales-call, qualification, b2b-sales, question-bank, objection-handling, prospecting]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - discovery call
  - discovery questions
  - qualification call
  - sales discovery
  - first call
  - intro call
  - sales agenda
  - question bank
  - call prep
  - prospect call
  - pain discovery
  - needs analysis
trigger_keywords:
  - prep me for a discovery call
  - build a question bank for this prospect
  - generate a discovery agenda
example_invocations:
  - "Prep me for a discovery call with the VP of Finance at a 1500-person logistics company. We sell AP automation."
  - "Generate a discovery agenda for a Head of Data at a Series B B2B SaaS. We sell a reverse-ETL product."
  - "Build a 30-minute question bank for a first call with a Director of CS at a healthcare platform. We sell an AI deflection layer."
inputs:
  - name: prospect_role
    type: text
    required: true
    description: Title and seniority of the prospect attending the call.
  - name: prospect_company_context
    type: text
    required: true
    description: Industry, size, stage, and anything you already know about the company.
  - name: our_category
    type: text
    required: true
    description: The product category we sell (e.g., "AP automation", "reverse-ETL", "AI deflection for support").
  - name: typical_outcomes
    type: text
    required: true
    description: The two or three outcomes our solution typically delivers, with rough numeric ranges.
  - name: call_length_minutes
    type: number
    required: false
    description: How long the call is (default 30). The agenda scales to fit.
  - name: known_signals
    type: text
    required: false
    description: Anything specific that triggered this call — inbound form fill, intent data, a referral, a public statement.
outputs:
  - name: agenda
    type: markdown
    description: A timed agenda for the call with each section's purpose.
  - name: question_bank
    type: markdown
    description: A categorized question bank covering current state, desired state, gap, decision process, success metrics, plus anti-questions to avoid.
  - name: objection_map
    type: markdown
    description: A list of objections this persona commonly raises, each mapped to a value driver and a sample bridging response.
  - name: next_steps_template
    type: markdown
    description: A short template for the recap email and the proposed next step.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill before a first or second sales call with a prospect, when the goal is to understand whether and how the product fits the prospect's situation, and to qualify them through to the next stage of the sales process. The skill produces a working document a seller can read in the five minutes before the call.

The skill is not a discovery framework lecture; it is a tailored artifact. It works best when the user can describe the prospect's role and company in a few sentences and can articulate the typical outcomes their product delivers. The richer the inputs, the sharper the questions.

Do not use this skill for closed-won customer kickoffs (those are implementation calls with a different shape), for renewal conversations (the customer already owns the product; questions change), or for cold qualifying outbound (the prospect has not consented to a call yet and a question bank will spook them).

## How to apply

Discovery is the highest-leverage skill in B2B sales. A well-run discovery call surfaces enough context that the seller can credibly tailor the next conversation, and surfaces enough business pain that the buyer wants to take the next conversation. A poorly-run discovery call sounds like an interview — and interviews end with "we'll let you know."

The methodology below is built around five domains of inquiry — current state, desired state, gap, decision process, success metrics — and supplements them with an "anti-questions" list (questions that sound discovery-like but actually destroy trust) and an objection-to-value map (so the seller can listen for objections and respond by reframing rather than rebutting).

### Step 1 — Read the inputs and identify the prospect's plausible mode

Buyers come to discovery calls in one of three modes, and each mode wants a different shape of conversation:

- **Browsing** — they are not yet sure they have a problem worth solving; they are sniffing the category. The call should over-index on insight-sharing, not interrogation.
- **Shopping** — they know they have a problem and they are talking to vendors. The call should over-index on differentiating context-fit; assume they have a checklist.
- **Buying** — they have already chosen the category and are narrowing to a vendor. The call should over-index on commercial mechanics: timing, decision process, success criteria.

Use the known signals input to infer the mode. An inbound form fill from a content-marketing page usually indicates browsing. A response to a competitor-mention outbound usually indicates shopping. A referral from an existing customer usually indicates buying. State your inference at the top of the agenda so the seller can adjust live if it turns out wrong.

### Step 2 — Build the timed agenda

Map the call length to a five-block structure. For a 30-minute call:

- **0:00–0:03 — Open and frame.** Thank them for the time, restate the purpose in one sentence, confirm the agenda, confirm the time available. ("My goal is to learn enough about how X works in your team to figure out whether we're worth a deeper conversation. I have a few questions, then we'll save 5 minutes for yours. Sound right?")
- **0:03–0:18 — Discovery proper.** Current state, desired state, gap. This is the substance of the call.
- **0:18–0:24 — Decision process and success metrics.** Often skipped on first calls — do not skip. Without these, the next call has no shape.
- **0:24–0:28 — Reframe what you heard plus a calibrated tease of relevance.** Not a pitch. Three sentences that demonstrate you listened.
- **0:28–0:30 — Next step.** Specific date, specific people, specific artifact.

Scale this proportionally for 45- or 60-minute calls; the discovery block expands, not the open or close.

### Step 3 — Generate the current-state question set

Current state is what the prospect's world looks like right now without your product. The job here is to surface:

- What workflow or system handles this today? (Process, tool, vendor, manual work.)
- How long has it looked like this? Has it changed recently? Why?
- Who touches this workflow most? (Helps you map the buyer center.)
- What does a representative day or week look like at the friction point?
- What metrics, if any, do you measure on this process today?

Ask one question at a time, then follow up with a why or a how. Avoid leading questions ("Don't you find that frustrating?"). Use neutral framings ("Walk me through last week.") that invite a story rather than a yes/no.

Generate five to seven current-state questions tailored to the persona. A VP of Finance gets questions about close cadence, vendor onboarding bottlenecks, and AP aging; a Director of CS gets questions about ticket volume by channel and triage SLAs; a Head of Data gets questions about pipeline failure rate and downstream consumer pain.

### Step 4 — Generate the desired-state question set

Desired state is what the prospect wishes their world looked like — independent of your product. Questions:

- If this worked perfectly six months from now, what would you see in the dashboard / report / inbox that you do not see today?
- What does "good" look like? What does "great" look like?
- Who at your company has the strongest opinion about how this should work?
- If you do nothing different for the next twelve months, what is the cost?

This last question is the one almost every seller forgets. It surfaces the cost of inaction — which is the real competitor in most B2B deals, not another vendor. If the prospect cannot articulate a cost of inaction, the deal will stall later.

Generate four to six desired-state questions. The seller's job here is to listen for emotion-bearing words: "frustrated", "stuck", "embarrassing", "missed quota", "missed milestone". Note those for the recap.

### Step 5 — Generate the gap question set

Gap is the space between current and desired state — and crucially, the prospect's own theory about why the gap exists. Many sellers skip this and jump straight to "here is why" — which deprives the prospect of the chance to own the diagnosis.

Questions:

- What have you tried so far?
- What worked, what didn't, and why do you think that is?
- Is there a workaround in place today? Who owns it?
- If you were to fix this with internal resources, what would it take?
- Is there a previous initiative that stalled out? What killed it?

The last question is critical. If a prior initiative died, the same forces will kill yours unless you understand them. "We tried this two years ago and it died in procurement" tells you the deal-killer for the next twelve months.

Generate four to six gap questions.

### Step 6 — Generate the decision-process question set

This is the section most sellers chicken out of on a first call. Asking about budget, authority, and timing feels intrusive. It is far more intrusive to spend three months building a deal that was never going to close.

Questions, asked gently:

- Walk me through how a decision like this typically gets made at your company. Who weighs in, who signs off?
- Has a budget been allocated, or is this an exploratory conversation?
- What would the timeline look like if everything went well? What would slow it down?
- Has anyone above you been briefed on this, or are you the first one looking?
- Is there a procurement or security review we should plan for?

Frame these as logistical, not interrogational ("So I can give you the right level of detail at the right time…"). If the prospect resists, do not push — note the resistance as a data point and circle back next call.

Generate four to six decision-process questions. Adjust to seniority — a VP can usually answer these directly; a Manager will often have to escalate, which itself is information.

### Step 7 — Generate the success-metrics question set

The point of this section is to make the prospect commit, on the call, to what success would look like — so you can write that into the recap and use it to structure every subsequent conversation.

Questions:

- If we were having a conversation six months after this deal closed, what would you want to be able to say it accomplished?
- What metric would you point your boss at?
- What number would tell you we failed?
- Is there a pilot or evaluation phase that fits your team's culture?

Generate three to five questions. The seller's job here is to write down the answer verbatim — the prospect's words become the next call's framing.

### Step 8 — Generate the anti-questions list

These are questions that sound like discovery but actually corrode the call. Provide them as an explicit "do not ask" list so the seller can self-correct:

- "What's your budget for this?" — too direct, too early. Replace with "Has a budget been allocated?"
- "Are you the decision-maker?" — concedes you did not research and insults their authority. Replace with the decision-process question above.
- "What are your pain points?" — corporate-speak that buyers do not use. Replace with "Walk me through last week."
- "Are you talking to anyone else?" — adversarial and not useful at this stage. Save for stage two.
- "What would it take to win your business?" — sounds like a vendor at a trade show. Replace with the success-metrics framing.
- "How can we help you?" — puts the burden on the buyer to do the work. Bring a hypothesis instead.

Tailor the anti-question list to the persona and category if there are domain-specific traps. For finance buyers, do not ask "What are you spending on this today?" before you have earned the right; for engineering buyers, do not ask "What stack are you on?" without context for why it matters.

### Step 9 — Build the objection-to-value map

Most discovery calls surface two or three predictable objections per persona. Pre-mapping them lets the seller listen for them and respond by reframing rather than scrambling. For each likely objection:

- Phrase it in the prospect's voice ("We've already tried something like this and it didn't work.").
- Identify the underlying concern (risk of repeat failure, sunk cost).
- Map it to a value driver our product offers (faster time-to-value, easier rollback, lower opportunity cost).
- Provide a one-sentence bridge ("That's exactly why most teams in your situation start with a 30-day evaluation — I'd want the same thing.").

Generate four to six objection maps tailored to the persona. Common patterns include:

- **Build-vs-buy** for engineering personas → reframe around opportunity cost of engineering time.
- **Vendor fatigue** for finance personas → reframe around tooling consolidation.
- **Change management** for ops personas → reframe around phased rollouts and existing-workflow compatibility.
- **Security and compliance** for any buyer at a regulated company → reframe around the security posture you bring (have specifics ready).

The seller should not ambush the prospect with these answers; the map is for listening, not interrupting.

### Step 10 — Draft the recap-and-next-step template

Most deals die between calls because nobody owns the next step. Pre-write the recap email template that the seller will send within two hours of the call ending:

- Two sentences thanking them and recapping what they said the success criteria are (their words, not yours).
- One sentence on the next step — specific date, specific time, specific artifact.
- One sentence on what the seller will bring (a tailored example, a security one-pager, a price range).

Pre-writing the template forces the seller to know on the call what they will commit to — which means they need to ask the right questions to be able to fill it in.

### Step 11 — Layer in the live-call coaching notes

Add a short "live coaching" block to the artifact — three or four reminders the seller can read while the call is happening:

- Talk under 30% of the time. The prospect should be doing most of the talking.
- After each answer, ask one follow-up before moving to the next category. "Tell me more about that" is the highest-leverage four words in sales.
- Write down emotion-bearing words verbatim. They become the recap framing.
- If you find yourself pitching, stop. The prospect did not ask for a pitch. Get back to questions.

### Step 12 — Output the artifact

Combine into a single markdown document with this structure:

- **Quick-scan summary** — the seller's mode inference, the top three questions to make sure they ask, and the one question they will most want to skip but should not.
- **Timed agenda.**
- **Question bank by domain** — current, desired, gap, decision, success.
- **Anti-questions.**
- **Objection-to-value map.**
- **Recap and next-step template.**
- **Live coaching block.**

The seller should be able to read the artifact in five minutes and have the top three questions memorized before the call starts.

### Step 13 — Calibrate to call number

Discovery is not always a single call. If the user indicates this is call two or call three, the question bank shifts:

- **Call one** — full breadth across all five domains. The goal is qualification and rapport.
- **Call two** — depth on whichever domain came up shallowest in call one (often decision process or success metrics). Bring tailored proof points.
- **Call three onward** — verification, not discovery. Have we confirmed each success metric? Have we identified every stakeholder? If yes, push to next stage. If no, pause the deal — chasing a deal with unresolved discovery debt is how stalls happen.

### Step 14 — Handle the multi-stakeholder case

If the input indicates more than one attendee, generate stakeholder-specific question routing:

- The economic buyer (often a VP or C-level): focus their questions on outcomes and success metrics.
- The user buyer (often a Manager or Director): focus their questions on current-state workflow detail.
- The technical buyer (often an Architect or Security lead): focus their questions on integration, security, and constraints.

Do not ask the user buyer about budget or the economic buyer about workflow detail; you will get bad answers and you will signal you do not understand who you are talking to.

### Step 15 — Refuse to invent context

If the inputs are too thin to tailor — e.g., "do a discovery call for a VP" with no company, no category, no signal — surface the gap and ask one focused question. Generic discovery agendas underperform tailored ones by a wide margin; the value of this skill is in the tailoring.

## Inputs

- **prospect_role** (required) — title and seniority.
- **prospect_company_context** (required) — industry, size, stage, observable facts.
- **our_category** (required) — product category in plain language.
- **typical_outcomes** (required) — outcomes with rough numeric ranges.
- **call_length_minutes** (optional, default 30) — drives the agenda scaling.
- **known_signals** (optional) — what triggered the call.

## Outputs

- A timed agenda for the call.
- A categorized question bank.
- An anti-questions list.
- An objection-to-value map.
- A recap and next-step email template.
- A short live coaching block.

## Examples

### Worked example — Head of Data at a Series B B2B SaaS, reverse-ETL category

**Inputs given to the skill:**

- prospect_role: "Head of Data, reports to CTO."
- prospect_company_context: "Series B B2B SaaS, 200 employees, ~$15M ARR, just hired their first analytics engineering manager last quarter."
- our_category: "Reverse-ETL — syncing modeled data from the warehouse to operational tools."
- typical_outcomes: "Cuts last-mile data engineering work 60%, gets sales and marketing teams self-serve on warehouse-modeled data."
- call_length_minutes: 30
- known_signals: "Inbound from a content piece on operational analytics; their analytics-engineering manager filled in the form."

**Output produced by the skill (abridged):**

**Quick-scan summary:**

- Inferred mode: between browsing and shopping. The hire of an analytics engineering manager last quarter is a real trigger; the inbound from content suggests they are researching the category but may not have a vendor list yet.
- Three questions to be sure you ask:
  1. "Walk me through how operational tools (CRM, marketing platform) get warehouse data today."
  2. "What did your team build internally before considering buying?"
  3. "If we were having this conversation in six months and it had gone well, what would the analytics eng manager be doing differently with their week?"
- The question they will skip but shouldn't: decision process, because this is an IC-led inbound and the procurement path is not obvious from the outside.

**Timed agenda:**

- 0:00–0:03 Open and frame.
- 0:03–0:10 Current state — how the warehouse-to-tools sync happens today.
- 0:10–0:16 Desired state — what would change if it worked.
- 0:16–0:21 Gap — what's been tried, what stalled.
- 0:21–0:26 Decision process and success metrics.
- 0:26–0:28 Reframe.
- 0:28–0:30 Next step.

**Question bank (current state, abridged):**

- Who currently owns the sync from your warehouse to operational tools?
- Walk me through the last time a sales or marketing user asked for a new field — what did the round-trip look like?
- How often does the data team get a "the data is stale" ping from a downstream team? Daily, weekly?
- What does your modeled-data layer look like — dbt, internal frameworks, both?
- Has anything broken recently that would not have broken if you had this kind of layer?

**Question bank (desired state, abridged):**

- If your analytics eng manager could spend zero time on operational sync, what would they spend that time on instead?
- What would self-serve look like for your sales or marketing teams in a world where this worked?
- If you do nothing different on this for 12 months, what's the cost?

**Question bank (gap, abridged):**

- What did the team build internally to handle this before considering buying?
- Is there a stalled project in this space? What killed it?
- Has anyone above you been briefed yet, or are you scoping?

**Question bank (decision process, abridged):**

- Is this an exploratory conversation or has a budget been earmarked?
- Walk me through how a tooling decision like this gets made — does it sit with you, with the CTO, or jointly?
- Is there a security or procurement review we should plan for? You're Series B — sometimes the formality is in flux at this stage.

**Question bank (success metrics, abridged):**

- If we were having this conversation in six months, what would you want to be able to say?
- What number would tell you it worked? What number would tell you it failed?
- Is there a pilot or trial pattern that fits how your team evaluates infrastructure?

**Anti-questions to avoid:**

- "What's your data stack?" (You should already have a hypothesis; if you don't, ask for it before the call.)
- "Are you the decision-maker?" (Replace with the decision-process question above.)
- "What pain points are you trying to solve?" (Replace with the workflow walkthrough.)

**Objection-to-value map (abridged):**

- "We built something internal that mostly works." → Concern is sunk cost. Bridge: most data teams who built internal versions still spend 5–15% of engineering time on maintenance; the question is whether that's the best use of analytics-eng time.
- "We're worried about losing control of the data layer." → Concern is governance. Bridge: lead with how the vendor sits on top of dbt models, not next to them — preserves the single-source-of-truth pattern.
- "Procurement is going to be slow." → Concern is process drag. Bridge: have the security one-pager ready before they ask; offer to do procurement intake before the technical eval.

**Recap email template:**

> Thanks for the time — really useful to walk through how your team handles operational sync today. To summarize what I heard: success in six months looks like [their words, fill in live]. The cost of doing nothing is [their words, fill in live].
>
> Next step: I'll send a tailored 20-minute walkthrough on [date], showing how the layer would sit on top of your existing dbt models. I'll bring [security one-pager / a similar-stage customer reference / a price range], so we can move forward efficiently if it fits.

**Live coaching block:**

- Talk less than 30% of the time.
- Write down emotion-bearing words verbatim.
- Do not pitch. If you find yourself explaining a feature, stop and ask another question.
- Confirm the next step before you hang up. Get a date on the calendar.

## Limitations

This skill produces a question bank tailored to the persona; it does not, by itself, conduct the call. The seller still has to listen, follow up, and adapt in real time. The artifact is a scaffold, not a script.

The skill cannot verify that the prospect's company description supplied by the user is accurate. If the user supplies wrong context, the questions will be tailored to the wrong situation. Verify the basics before the call (size, stage, vertical, recent triggers).

The objection-to-value map is a pre-call hypothesis, not a guaranteed prediction. Personas vary inside categories; if the live call surfaces an objection that was not on the map, the seller should not force the canned bridge — they should listen, reflect it back, and explore. Mapped objections are starting points, not endings.

Discovery norms vary by region and culture. In some markets, asking about budget or decision process on call one is welcomed; in others, it is considered rude until trust is established. The skill defaults to North American B2B norms; sellers in other markets should adjust pacing.

The skill does not handle objection rebuttals at depth. It maps each objection to a bridge — the seller still has to handle the follow-up conversation. For deeper objection handling, pair this skill with a separate methodology focused on negotiation and competitive defense.

## Sources reviewed

- https://github.com/filip-michalsky/SalesGPT
- https://github.com/alirezarezvani/claude-skills
- https://github.com/ericosiu/ai-marketing-skills
- https://github.com/sales-skills/sales
- https://github.com/phuryn/pm-skills
- https://github.com/ethanplusai/harvey
- https://github.com/topics/sales-prospecting
