---
id: skillsgit-curated/sourcing-message-crafter
version: 1.0.0
name: Sourcing Message Crafter
description: Writes a short, relevant, non-creepy outreach message to a passive candidate, anchored to specific evidence from the candidate's public work and the recruiter's role context.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: hr
tags: [niche:recruiting-hiring, sourcing, passive-candidate, outreach, recruiter-messaging, talent-acquisition, personalization]
license_type: free
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 16000
  estimated_tokens_per_invocation: 4000
trigger_keywords:
  - write a sourcing message
  - inmail to candidate
  - recruiter outreach
  - passive candidate
  - sourcing email
  - cold message candidate
  - personalize outreach
  - linkedin recruiter message
  - referral message
  - re-engage candidate
example_invocations:
  - "Draft a sourcing message to a senior backend engineer at a competitor; here's their GitHub and LinkedIn."
  - "Write an InMail to a passive product manager candidate referencing their conference talk."
  - "Re-engage a candidate we passed on six months ago for a different role."
inputs:
  - name: candidate_evidence
    type: text
    required: true
    description: Specific public evidence about the candidate that you can credibly reference — a project, a talk, a published article, a contribution, a job change. The more specific the better.
  - name: role_context
    type: text
    required: true
    description: The role being offered, including title, team, and one or two distinctive things about the work that would be true and relevant for this candidate.
  - name: candidate_seniority
    type: text
    required: true
    description: The candidate's likely seniority level. Calibrates tone, length, and what kind of bait to use.
  - name: company_context
    type: text
    required: false
    description: Brief context about the hiring company that is non-obvious — recent funding, a credible technical or commercial milestone, a specific reason the candidate might care now.
  - name: relationship_context
    type: text
    required: false
    description: Any prior relationship — a past application, a mutual connection, a previous interview at the company, a referral source.
  - name: channel
    type: choice
    required: false
    description: The channel the message will be sent through.
    choices: [linkedin_inmail, email, referral_intro, follow_up]
outputs:
  - name: message
    type: markdown
    description: A single short outreach message calibrated to the candidate and channel.
  - name: subject_variants
    type: markdown
    description: For email channels, three to five subject line options labeled by hypothesis.
  - name: rationale
    type: markdown
    description: A brief rationale naming the personalization anchor, the framing chosen, the ask used, and what would change the message.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a recruiter, hiring manager, or sourcing partner needs to write outreach to a specific named candidate who is not actively in the company's pipeline. The skill is calibrated for one-to-one outreach where the sender will read every draft, edit if needed, and send personally — not for bulk sequences fired at hundreds of recipients.

The skill works for several adjacent use cases:

- **Cold outreach to a passive candidate** the recruiter has identified through sourcing.
- **Re-engagement of a previously passed-on candidate** for a different or evolved role.
- **A warm intro draft** for a referrer to send into their network.
- **A second-touch follow-up** after a candidate did not respond to a first message.

Do not use this skill for high-volume sourcing where each recipient gets a templated form letter. The methodology assumes a real evidence anchor per recipient; without one, the message reverts to generic recruiter-speak that strong passive candidates filter out without reading. Do not use it for active candidates already in the pipeline; the right communication to them is the recruiter's scheduling and update sequence, which has different conventions.

Do not use this skill where the candidate has expressed any signal of not wanting to be approached (a "no recruiters" line in their bio, an explicit prior decline). Respecting that is both ethically right and practically smarter; ignored signals damage the recruiter's and the company's reputation across the candidate's network.

If the candidate_evidence input is generic ("active LinkedIn user", "Senior Engineer at Company X"), surface the gap before drafting. The single most reliable predictor of a passive-candidate response is whether the recruiter has done credible homework on the recipient. The message can only reflect the homework that was done.

## How to apply

Most sourcing outreach is ignored. Strong passive candidates receive multiple recruiter messages a week, often per channel, and have evolved sophisticated filters for what is worth reading. The methodology below addresses the failure modes that make outreach get filtered out.

### Step 1 — Identify the candidate evidence anchor

The single most important sentence in any sourcing message is the one that demonstrates the recruiter has read something specific about the candidate. The strength of that sentence determines whether the rest of the message gets read.

Strong evidence anchors:

- A specific project the candidate built or contributed to substantially, named with enough detail that the candidate can tell the recruiter looked at the project, not just the title.
- A specific talk, paper, or article the candidate authored, referenced for what it said, not that it exists.
- A specific past role transition the candidate made, framed in terms the candidate would themselves use to explain the move.
- A specific peer or collaborator named, with an honest framing of how the recruiter learned about them through that connection.

Weak evidence anchors to avoid:

- "I saw your impressive background" — generic and tells the candidate nothing.
- "You are a Senior X at Y" — restating the candidate's own resume back to them is not personalization.
- "I came across your profile" — true of everyone, signals nothing.
- "Your role at [previous company] caught my eye" — too vague to demonstrate real reading.

If the candidate_evidence input does not support a strong anchor, surface that gap before drafting and ask one focused question about what specifically the recruiter knows about the candidate.

### Step 2 — Reject the impulse to invent

Recruiters under volume pressure invent specificity. They claim to have read a project they have not opened. They reference a conference talk they only saw the title of. The candidate notices, often within the first reply, and the recruiter and company lose credibility across that candidate's network.

The methodology hard-rules against invention: if the recruiter does not have a specific evidence anchor, the message either acknowledges its own genericness honestly or does not get sent. Most experienced passive candidates respect an honest, short, role-relevant message more than a manufactured-personalization one.

### Step 3 — Calibrate length to seniority and channel

Length conventions that hold up:

- **LinkedIn InMail to a senior candidate (Director+ or staff-track IC).** 90 to 150 words. They get many; the short ones read.
- **LinkedIn InMail to a mid-level candidate.** 100 to 180 words. Slightly more context on the role helps because the candidate is more likely earlier in active consideration.
- **Email to a senior candidate.** 120 to 200 words. Email allows slightly more length than InMail because the candidate self-selected to open it.
- **Referral intro draft.** Short — 60 to 100 words. The referrer adds their own context; the draft is a starting point.
- **Re-engagement of a prior candidate.** 90 to 130 words. Acknowledges the prior context briefly and pivots to what has changed.

Messages over 300 words on any channel see sharp drop-offs in completed-read rates. There are limited exceptions — a very senior IC hire for a deeply technical role can tolerate a longer message if the technical specificity earns it — but the default is short.

### Step 4 — Structure the message in four moves

A defensible sourcing message has four parts:

1. **Anchor.** The evidence-specific opening. One to two sentences. Demonstrates homework without performing.
2. **Bridge.** Why the role is relevant to this specific candidate's trajectory. One to two sentences. This is the part most messages skip.
3. **Pitch.** Two to three concrete reasons the role might be worth a conversation. Specific, not generic.
4. **Ask.** One small request — usually a 15- to 20-minute conversation, sometimes an even smaller "would it be useful to send the JD".

This four-move structure does not mean four paragraphs. In a short message it can be one or two paragraphs with the moves run together. The order matters more than the paragraph structure.

### Step 5 — Open with the anchor, not the sender

The first line is about the candidate, not the recruiter. Never:

- "I hope this finds you well." Filler; trains the filter.
- "I'm a recruiter at X." The candidate can see who you are; this opening squanders the first read-line.
- "I noticed you are the Senior Engineer at Y." Restates known information.

Always:

- A specific reference to the candidate's work or recent move.
- A specific observation that demonstrates familiarity with the candidate's domain at the level the candidate operates in.

### Step 6 — Bridge to the candidate's trajectory

The bridge is the bridge between what the recruiter knows about the candidate and why this role might matter. The strongest bridges name something about the candidate's likely current state and connect it credibly to the role.

Examples of bridges that work:

- "Three years at [current company] is the median tenure for engineers at your level there before they look; if you are inside that window, the next move usually weighs heavily on the technical surface area." [Then bridge to what surface area this role offers.]
- "Your recent talk on [topic] suggested you are working through [specific problem]; this role is one of the few in the market where that problem is the day-job rather than a side concern."
- "You did the [specific kind of transition] last time you moved, which is the same shape of move this role offers — but in a context where [specific differentiator]."

Bridges that fail:

- "I think you'd be a great fit." Empty without evidence.
- "Your skills match what we're looking for." Restates the recruiter's framing as if it were the candidate's.

If the recruiter cannot construct a bridge from the evidence available, the message should pivot to honest brevity rather than fake bridging.

### Step 7 — Pitch with concrete role facts, not adjectives

The pitch is three to four very short, very specific facts about the role. Adjective stacks ("a great team", "exciting work", "an amazing opportunity") read as marketing copy. Concrete facts read as a real role:

- The team's specific scope and mandate.
- A current concrete problem the role would own — named at the right level of resolution for the candidate's seniority.
- A specific operating-condition fact: comp band, remote policy, equity, stage, on-call shape.
- A specific cultural or strategic fact that the candidate could not get from the public-facing careers page.

Three to four facts is the right density. Five or more shifts the message from a curiosity-prompt to a brochure; the candidate stops reading.

### Step 8 — Ask small

The right ask at touch one is a 15- to 20-minute conversation. Smaller asks ("does this sound interesting to you", "happy to send the JD if you want") are also fine and often win on response rate. Larger asks ("would you like to interview", "what is your availability for an onsite") are out of scale for cold outreach and reduce response rates.

Phrasings that work:

- "Worth a 20-minute call?"
- "If you'd like the role details, I can send a one-pager."
- "Would it be useful to know more, or is this not a moment in your career when a move would make sense?"

The last phrasing — explicit permission to say no — consistently improves response rates because it acknowledges the candidate's agency and removes the pressure to respond at all.

### Step 9 — Calibrate compensation transparency

In jurisdictions with pay-transparency requirements (and increasingly outside them), including a comp band in the sourcing message is both legally appropriate and commercially smart. Senior passive candidates frequently filter on comp before they reply; messages without bands get filtered.

For senior candidates, include a base salary range (and equity range if material) in the pitch. For more junior candidates, comp is often deferred to the recruiter call, but a "comp is competitive at the senior end of [city]'s market" line is too generic to count as transparency.

### Step 10 — Avoid the standard creepy patterns

Several patterns reliably read as creepy and corrode reply rates:

- **Over-familiarity.** First-name informality on a first contact with a senior candidate often reads as presumptuous; for some candidates and cultures it is normal. Default to the candidate's professional cues — if their public bio uses last names and titles, mirror that.
- **Performative empathy.** "I imagine you're really busy" and "I know how it feels" from a stranger reads as theater.
- **Manufactured urgency.** "We're closing the role on Friday" is rarely true and read as pressure tactics.
- **Implicit comparison to the current employer.** "I know things must be tough at [current company]" presumes facts about the candidate's experience. Even if the comparison is true, the candidate did not invite the recruiter into that judgment.
- **Aggressive follow-up cadence.** Three messages in five days from a recruiter the candidate has never met reads as harassment; two messages with a week between them is usually the upper bound.
- **Mass-mailed personalization tokens.** "[Hi {{first_name}}]" or visibly templated openings signal the message is one of many; senior candidates filter on that alone.

### Step 11 — Subject lines (email only)

For email channels, draft three to five subject line options. Recurring high-performing patterns:

- **Reference the candidate's domain in their language.** "your work on [specific project area]" beats "an opportunity at [company]".
- **Use the candidate's name in third position, not first.** "[topic], [verb], [name]" patterns outperform "[name], [topic]" because the candidate scans the first two words before personalizing.
- **Avoid corporate signal words.** "Exciting opportunity", "career-changing", "exclusive" — all trigger inbox-filtering.
- **Lowercase often outperforms title case** for engineering and technical audiences; CFOs and senior commercial roles expect title case.
- **Length under 50 characters.** Anything longer truncates on mobile.

Label each subject line by hypothesis: what the recruiter is testing if they send the message and the recipient does or does not open.

### Step 12 — Handle the re-engagement case

When the candidate previously interviewed or was sourced and declined, the methodology changes:

- Acknowledge the prior contact briefly and honestly. ("I appreciated the conversation last fall.")
- Name what has changed since then. The right reasons to re-reach include: a new role that fits better, a meaningful change in the company's situation, a meaningful change in the candidate's situation that you know about.
- Do not pretend the prior contact did not happen.
- Offer easy exit: "If timing or fit is still off, the answer is the same I'd respect last time. No follow-up beyond this note."

Re-engagements that work treat the candidate as a person whose answer six months ago was a real answer that may now have a real update; re-engagements that fail treat the candidate as a slot in the pipeline who just needs to be hit again.

### Step 13 — Output the message and the rationale

The deliverable is the message itself, plus a short rationale paragraph for the recruiter:

- Which evidence anchor was used and why.
- Which framing (curiosity, trajectory, problem) was chosen.
- Which seniority and channel conventions were applied.
- One sentence on what would change the message if the recruiter learned a specific additional fact about the candidate.

The rationale is for the recruiter's calibration and editing; it does not get sent to the candidate.

### Step 14 — Refuse to fabricate

If the recruiter has not provided evidence specific enough to anchor, the skill outputs a structured request for what additional evidence would help, alongside a generic but honest fallback message that explicitly does not invent specificity. The recruiter chooses whether to send the fallback or to invest in better sourcing before sending.

## Inputs

- **candidate_evidence** (required) — specific public evidence about the candidate.
- **role_context** (required) — the role's distinctive elements.
- **candidate_seniority** (required) — for tone, length, and ask calibration.
- **company_context** (optional) — non-obvious facts about the hiring company.
- **relationship_context** (optional) — prior interactions or referral chain.
- **channel** (optional) — InMail, email, referral intro, or follow-up.

## Outputs

- A single calibrated outreach message.
- Subject line variants for email channels.
- A short rationale on the personalization anchor and the framing chosen.

## Examples

### Worked example — Senior Backend Engineer at a competitor, InMail

**Inputs given to the skill:**

- candidate_evidence: "Maintains a popular open-source library for Postgres connection pooling, recently posted on their blog about scaling a payments service from 200 to 2000 transactions per second. Tenure at current employer just passed three years."
- role_context: "Senior backend engineer on a payments platform team at a Series B fintech, the team owns ledger and settlement, comp $180-220k, fully remote in the US."
- candidate_seniority: "Senior IC, likely 6-9 years experience."
- company_context: "Series B, profitable, last raise was top-up not survival."
- relationship_context: "None."
- channel: "linkedin_inmail"

**Output produced by the skill:**

> Your write-up on scaling the payments service from 200 to 2,000 TPS — particularly the section on connection pool sizing under bursty load — is the cleanest piece I've read on that problem in months. Your pgbouncer wrapper has been on my radar for a while.
>
> Three years in is when most engineers at your level start weighing surface area for the next move. We're hiring a senior backend engineer on the payments platform team at [Company]. The team owns the ledger and settlement infrastructure end-to-end; the role would partner on the next-generation ledger partition as we double transaction volume in the next year. Comp band $180k-$220k base plus meaningful equity, fully remote US, the team has a culture of design docs and humane on-call.
>
> Worth a 20-minute conversation in the next two weeks? Happy if the answer is "not this year" — I'd just rather ask than assume.

**Subject variants (not applicable for InMail; included anyway as example):**

- "your pgbouncer wrapper and a ledger problem" — hypothesis: domain reference plus problem cue.
- "scaling payments past 2k tps" — hypothesis: number-led, no name in subject.
- "the next ledger partition" — hypothesis: short, problem-led, intrigues without selling.

**Rationale:**

Evidence anchor: the candidate's specific blog write-up and open-source library, named at a level of detail that demonstrates the message was not auto-generated. Framing: trajectory bridge (three years in is the typical move window for this seniority on this track) plus problem (ledger partition is the kind of work the candidate's recent writing suggests interest in). Comp transparency: numeric range, not "competitive". Ask: 20-minute conversation, with explicit permission to say no. If the recruiter learned the candidate had recently been promoted, the framing would shift away from trajectory-driven and toward problem-fit only.

## Limitations

This skill writes the message; it does not source candidates, verify the evidence is real, or check that the recipient's contact information is current. The recruiter is responsible for the sourcing rigor that produced the inputs and for the deliverability layer.

The skill assumes a one-to-one workflow. It is not safe to wire into a fully automated bulk-send pipeline; the personalization anchor depends on real per-candidate evidence, and at high volume the evidence quality degrades faster than any quality-control loop can catch.

The skill cannot detect that the candidate has signaled "no recruiters" if that signal lives somewhere the recruiter did not provide as input. The recruiter is responsible for respecting opt-out signals.

The skill produces a single message. It does not produce a multi-touch cadence. For repeated outreach to the same candidate, the same skill can be invoked with relationship_context describing the prior message; the methodology will treat the second message as a re-engagement.

The skill does not validate compensation legality. Pay-transparency laws differ by jurisdiction; the recruiter and in-house counsel are responsible for confirming any included comp band meets local requirements.

Recruiter outreach norms shift. Filter sensitivity to certain phrases and patterns evolves quarterly; what reads as personal in one season reads as templated in the next. Skills like this need refreshing as norms shift.

## Sources reviewed

- https://github.com/cockroachlabs/open-sourced-interview-process
- https://github.com/sourcegraph/handbook
- https://github.com/yangshun/tech-interview-handbook
- https://github.com/clef/handbook
- https://github.com/hkdobrev/awesome-handbooks
- https://github.com/Assystant/SpotAxis
