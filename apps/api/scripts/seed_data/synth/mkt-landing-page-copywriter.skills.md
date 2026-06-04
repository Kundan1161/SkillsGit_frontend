---
id: skillsgit-curated/landing-page-copywriter
version: 1.0.0
name: Landing Page Copywriter
description: Given a product or feature, an ideal customer profile, and an offer, produce above-the-fold copy, value props, objection handling, social proof, and CTAs arranged into a tested page structure.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [copywriting, landing-page, conversion, cro, saas, headline, value-prop, cta]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - landing page
  - hero copy
  - above the fold
  - value proposition
  - headline
  - subheadline
  - CTA copy
  - social proof
  - conversion copy
  - SaaS page
  - feature page
  - pricing page copy
  - homepage copy
  - waitlist page
example_invocations:
  - "Write the landing page copy for our new error-tracking product aimed at platform engineers at $50M ARR companies."
  - "Rewrite our homepage hero to lean into the free trial instead of the demo."
  - "Draft a waitlist page for our AI underwriting tool for mortgage brokers."
  - "Build a feature page for our new audit-log export, targeted at security leads."
inputs:
  - name: product
    type: text
    required: true
    description: What the product or feature does, in plain English, with the technical underpinnings if relevant.
  - name: icp
    type: text
    required: true
    description: Ideal customer profile — role, company stage, the moment in their work when the product matters, and what they are using today.
  - name: offer
    type: text
    required: true
    description: What the visitor is being asked to do (start free, book demo, join waitlist, request access, buy now) and any sweetener (credit, money-back, lifetime).
  - name: positioning
    type: text
    required: false
    description: Optional category claim, alternative, or "X for Y" framing. If omitted, the skill proposes one.
  - name: proof
    type: text
    required: false
    description: Customer names, logos, metrics, awards, certifications, or testimonials the page can cite.
  - name: tone
    type: choice
    required: false
    description: Voice register. Defaults to "direct."
    choices: [direct, warm, playful, technical, formal]
  - name: page_type
    type: choice
    required: false
    description: Which page archetype to produce.
    choices: [homepage, product, feature, pricing, comparison, waitlist, signup, integration]
outputs:
  - name: page_copy
    type: markdown
    description: Section-by-section copy with explicit section labels, ready to drop into a CMS or design comp.
  - name: rationale
    type: markdown
    description: Per-section commentary explaining the persuasion choice, with two or three A/B variants for the highest-leverage elements.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Landing Page Copywriter

## When to use

Use this skill when a team needs the words for a page they will design and ship, not a discussion of strategy. It works for new product launches, refresh of an aging homepage, feature pages that support a release, comparison pages targeting a specific competitor or alternative, pricing pages where the copy carries as much weight as the table, waitlist or pre-launch pages, integration partner pages, and post-event landing pages tied to a campaign.

The skill assumes the reader of the output will be a designer, a developer, or a marketer pasting into a CMS. It produces copy organized by named sections that match the conventions used by the most widely adopted open-source SaaS landing templates. Skip it when the work is purely visual (no copy decisions), when the page is a long-form article (use the blog post skill), or when the artifact is an email or ad creative.

## How to apply

1. **Establish the conversion contract.** Write a single sentence that names: who the visitor is, what they want before they arrived, what they will be asked to do, and what they get if they do it. Every later section is graded against this sentence. If the user did not supply the offer in actionable terms, ask one clarifying question — what is the literal button text, and where does it go?
2. **Identify the level of awareness.** Visitors arrive somewhere on a five-rung ladder: unaware of the problem, problem-aware, solution-aware, product-aware, most-aware. A homepage typically targets problem-aware to solution-aware. A feature page typically targets product-aware. A waitlist or comparison page targets most-aware. The hook, the proof type, and the CTA aggressiveness all shift with awareness.
3. **Choose the leading angle.** From the product, ICP, and offer, derive one of four angles: outcome ("get X faster / cheaper / safer"), identity ("for teams who care about Y"), mechanism ("we do it differently because Z"), or contrast ("not like the legacy tool you already know"). Pick one as the dominant frame; the others may appear as secondary support but do not compete for the headline.
4. **Draft the hero.** The hero is three to five elements: an eyebrow (optional, sets context — category, badge, version, target audience), a headline (the angle in one sentence), a subheadline (the proof or mechanism in one or two sentences), a primary CTA button label, and an optional secondary CTA. The headline is not a tagline; it is a promise the rest of the page must keep.
5. **Generate three headline variants.** Vary by angle, not by synonym. Variant A is the outcome version. Variant B is the mechanism version. Variant C is the identity or contrast version. Annotate each with the target awareness rung and the trade-off (specificity vs. reach).
6. **Write the subheadline to absorb the obvious skepticism.** The reader will instinctively ask "okay, but how?" or "okay, but for whom?" — the subheadline answers one of those without padding. Avoid restating the headline.
7. **Pick the primary CTA label by friction.** "Start free" is appropriate when self-serve is real and onboarding is short. "Book a demo" is appropriate when the buy is consultative. "Get the report" or "Join the waitlist" reduces friction when the product is not yet ready. The button label is the second-most-edited element on the page after the headline; treat it as a sentence, not an afterthought.
8. **Place a social proof bar directly under the hero.** A row of logos with one line of context ("Trusted by engineering teams at…"), or a single quote with attribution, or a number ("12,000 developers shipped with X last month"). Use what you have; do not fabricate. If the proof is thin, replace the bar with a credibility signal that is true (a security cert, a relevant integration, a known investor) — and only if it is actually a credibility signal to the ICP.
9. **Structure the value-prop block as three or four payoffs.** Each payoff is a short headline (verb-led or noun phrase, parallel form), a one- or two-sentence body, and an icon slot. Order them by the visitor's question sequence: what does it do, who is it for, why is it different, how fast can I see value. Resist listing more than four; readers stop counting.
10. **Show, do not tell, with a "how it works" or product visualization.** Three steps is the default cadence. Each step has a label, a one-line action, and a visual (annotated screenshot, mini-diagram, or animated frame description). Steps are short imperatives in present tense.
11. **Add a feature grid only if the page is feature-led.** Use a feature grid for product pages aimed at evaluators. Six to nine cells, each with a one-phrase label and a one-sentence explanation. Group by job-to-be-done, not by component name.
12. **Insert a midpage social proof section.** This is heavier than the hero bar: one or two full testimonials with name, title, company, and outcome metric; a customer logo wall organized by segment; or a short case-study teaser with a measurable headline ("Acme cut on-call hours by 64% in 90 days") and a link.
13. **Engineer the objection-handling section.** List the four to seven objections the ICP will surface, ordered by frequency. Common archetypes: "is this for our size?" (segment fit), "is it secure / compliant?" (risk), "what does it cost?" (pricing transparency), "do we need to rip and replace?" (switching cost), "what about [competitor]?" (alternative comparison), "how long until we see value?" (time to value), "what if it doesn't work?" (reversibility — trial, refund, exit). Place the answers either as an FAQ section or as inline mini-sections, depending on visual real estate. Each answer is two sentences and one supporting detail.
14. **Treat pricing as copy.** If the page includes pricing, write a line above the plans naming the unit ("per seat," "per project," "based on usage") and a one-line decision aid ("most teams start on Pro"). Each plan needs a one-phrase identity ("for solo builders") and three to five inclusions written as benefits, not features. The "talk to sales" plan gets a one-sentence trigger ("when you need SSO, custom contracts, or annual procurement").
15. **Add a final CTA section that re-states the contract.** The closing CTA is a one-sentence reaffirmation of the offer ("Start free, no credit card. Upgrade only if your team sticks."), the primary button, and either a secondary "see pricing" / "talk to us" link or a low-stakes alternative ("read the docs"). Do not introduce new arguments here; readers who scrolled this far have decided whether to convert.
16. **Write the footer microcopy.** A footer is more than navigation. Include: a one-sentence company line, a status link, a security or trust center link if applicable, a careers link, a legal cluster (terms, privacy, DPA), and language for the cookie banner if regulatory geographies apply. Keep tone consistent — the footer is where credibility quietly accumulates or quietly leaks.
17. **Compose meta and social tags.** Page title (≤60 chars, brand at the end), meta description (≤155 chars, the headline reframed plus a verb), OG title (more emotional than meta title), OG description, OG image concept (one sentence), Twitter card type. The meta description is read more often than the headline by people who never click; write it last but write it deliberately.
18. **Add accessibility cues to the copy.** Alt-text drafts for every image slot; button labels that make sense out of context (avoid "click here"); ARIA labels for icon-only buttons; clear focus states implied by the structure. Accessibility is not a separate pass — it is a property of well-written copy.
19. **Generate two A/B variants for the highest-leverage elements.** Always: the headline. Often: the primary CTA label. Sometimes: the first value-prop. Provide each variant with a one-line hypothesis ("Variant B should outperform when the visitor is solution-aware because it leads with mechanism, not outcome").
20. **Audit for the four landing-page failure modes.** (a) Vague headline — replace any sentence that survives a swap with the competitor's product. (b) Stacked CTAs of equal weight — one button must dominate. (c) Proof without specificity — replace "trusted by leading teams" with named logos or a number. (d) Feature creep — if a section does not move the conversion contract forward, cut it.
21. **Run a "five-second test" review.** Read only the hero. A visitor seeing this for five seconds should be able to say what the product is, who it is for, and what to do next. If not, rewrite the headline or subheadline.
22. **Run a "F-pattern" review.** Eye-tracking research suggests visitors skim the top, then the left edge, then a horizontal band lower on the page. Make sure the left-edge first words of each section carry the argument. Avoid leading sections with filler like "We believe…" or "In today's market…".
23. **Match length to friction.** A free signup page is short; the visitor has decided. A demo-request page on a $50k ACR product is longer; the visitor needs more reassurance. As a rule, the length of the page tracks the price and reversibility of the offer.
24. **Honor the visual grammar of the page type.** Homepages have a hero, a "what we do" band, a "who we serve" band, social proof, and a final CTA. Feature pages drop the segmentation and elevate the demo. Comparison pages lead with a table and tuck differentiation into post-table copy. Pricing pages lead with the plans and answer "but…" objections below. Waitlist pages strip everything except the promise, the proof of seriousness (founders, funders, beta access), and the form.
25. **Write to the spoken voice of the audience, not the writer's voice.** Re-read the draft as if the ICP is in the room. Any sentence that sounds like a vendor and not like a peer should be flagged for revision. Replace acronyms the ICP does not use; explain acronyms the ICP does use only on first appearance and only when the audience spans seniorities.
26. **Return two artifacts.** The page copy is organized by section label, with each section starting with a level-2 heading naming the section and a fenced summary of what each element should do, followed by the copy itself. The rationale document mirrors the same section labels and explains the why and the variants. Separating the two lets the design team consume one and the growth team consume the other.

## Inputs

- `product` — what it does, in plain language, with any technical specifics that matter to the ICP.
- `icp` — role + stage + situation + status-quo tool.
- `offer` — exact button-level ask plus any sweetener.
- `positioning` (optional) — claimed category, "X for Y" framing, or competitor contrast.
- `proof` (optional) — logos, testimonials, metrics, certifications.
- `tone` (optional) — direct, warm, playful, technical, formal.
- `page_type` (optional) — homepage, product, feature, pricing, comparison, waitlist, signup, integration.

## Outputs

- A section-by-section page copy document: hero, social proof bar, value-prop block, how-it-works, feature grid (conditional), midpage social proof, objection handling / FAQ, pricing (conditional), final CTA, footer microcopy, meta and OG tags.
- A rationale document with the persuasion logic per section and at least two A/B variants for the headline and primary CTA.

## Examples

**Example 1: SaaS homepage refresh, solution-aware audience.**

*Input* — product: error monitoring for distributed systems; icp: platform engineering leads at Series B-D; offer: 14-day free trial, no credit card; tone: technical-direct.

*Hero output sketch* — Eyebrow: "Built for platform engineers." Headline (recommended variant): "Find the bug before the on-call call." Subheadline: "Correlate traces, logs, and deploys in one place — so 'who broke what' takes thirty seconds, not three hours." Primary CTA: "Start free trial." Secondary: "See a live example." Social proof under hero: a logo bar with one line ("Trusted by platform teams at Acme, Globex, and Initech."). A/B variant headline: "On-call should not feel like detective work." Rationale variants: A leads with outcome (lower MTTR); B leads with identity (the lived experience of being on-call). A is broader; B converts better on second visits from solution-aware visitors.

**Example 2: Comparison page, most-aware audience.**

*Input* — product: developer-first analytics tool; icp: founders evaluating a switch from a dominant incumbent; offer: book a 30-minute migration call; page_type: comparison.

*Output sketch* — Hero headline: "Five reasons teams move from [Incumbent] to [Product] — and one reason they don't." Below: a comparison table by job (event modeling, query speed, billing predictability, schema ownership, support responsiveness). After the table: a numbered list of the five reasons, each grounded in a customer quote slot (with `// note: replace with real quote`). Objection handling: dedicated section addressing "but our analysts are trained on [Incumbent]." Final CTA: "Book a 30-min migration call — we will tell you if it is not worth switching." Variant for the CTA label: "Get a migration estimate." Rationale: the more reversible-sounding CTA outperforms when the prospect has switching cost anxiety.

**Example 3: Pre-launch waitlist page.**

*Input* — product: an AI underwriting copilot for mortgage brokers; icp: independent mortgage brokers; offer: join waitlist for paid pilot in Q3.

*Output sketch* — Strip the page to four blocks. Hero: "Underwrite a clean file in twenty minutes." Subheadline: "Quote, qualify, and document with a copilot that knows your lender matrix." Trust block: a one-liner with founder names and a previous-company credential (only if true). One short value-prop trio (faster decisions, fewer touchpoints, lender matrix kept current). Form with three fields (name, work email, NMLS ID) and a CTA "Request pilot access." Footer: a line on data handling and a privacy link. Rationale: a waitlist page is a promise, not a product page; resist adding feature grids until there is a product to demo.

## Limitations

- The skill does not run A/B tests; it produces variants and hypotheses. Real significance comes from your traffic.
- Pricing transparency choices (publish vs. "contact us") depend on commercial strategy the skill cannot infer.
- Highly regulated industries (medical claims, financial advice, securities) require legal review for claims like "guaranteed," "FDA-approved," "no risk," and similar.
- The skill assumes a Western, English-speaking audience; copy for other markets should be localized with cultural review, not machine-translated.
- The skill produces copy, not visual hierarchy decisions; final spacing, typography, and layout choices belong to the designer.
- If the product is genuinely undifferentiated, the skill will surface that rather than invent claims; expect a flag in the rationale section, not a fictional differentiator.
- Brand voice guidelines, if supplied, override the default tone choices; without them, the skill applies the conventions common to modern open-source SaaS landing templates.

## Sources reviewed

- https://github.com/PaulleDemon/awesome-landing-pages
- https://github.com/leoMirandaa/shadcn-landing-page
- https://github.com/Adrinlol/landy-react-template
- https://github.com/Blazity/next-saas-starter
- https://github.com/saas-js/saas-ui-nextjs-landing-page
- https://github.com/f/awesome-chatgpt-prompts
- https://github.com/langgptai/awesome-claude-prompts
- https://github.com/aminblm/awesome-chatgpt-content-creation-prompts
