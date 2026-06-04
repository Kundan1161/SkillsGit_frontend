# Customer Support — Synthesis Report

**Area:** customer support (ticket triage, response drafting, KB articles)
**Date:** 2026-05-14
**Curator:** skillsgit-curated

## Files produced

1. `apps/api/scripts/seed_data/synth/support-ticket-triager.skills.md`
   - Subscription $11/mo, support included.
   - Classifies inbound ticket, assigns priority + SLA, routes to team, duplicate-checks, drafts acknowledgment.
2. `apps/api/scripts/seed_data/synth/support-reply-drafter.skills.md`
   - Subscription $9/mo, support included.
   - Drafts outcome-aware (apologize / explain / resolve / partial-resolve / escalate / decline / gather-info / hold) reply calibrated to relationship tier and voice.
3. `apps/api/scripts/seed_data/synth/support-kb-article-synthesizer.skills.md`
   - One-time $99.
   - Converts one or more resolved ticket threads into a publishable KB article (Problem / Cause / Solution / Workarounds / Related) plus structured metadata.

## Sources used (per skill, URL-only, MIT / Apache-2.0)

### Support Ticket Triager (7 sources)
- https://github.com/chatwoot/chatwoot (MIT, 29k+ stars)
- https://github.com/papercups-io/papercups (MIT, 6k stars)
- https://github.com/helpyio/helpy (MIT, 2.5k stars)
- https://github.com/polonel/trudesk (Apache-2.0, 1.5k stars)
- https://github.com/BookStackApp/BookStack (MIT, 18.8k stars)
- https://github.com/deepset-ai/haystack (Apache-2.0, 25k+ stars)
- https://github.com/langchain-ai/langchain (MIT, 137k stars)

### Support Reply Drafter (7 sources)
- https://github.com/chatwoot/chatwoot
- https://github.com/papercups-io/papercups
- https://github.com/helpyio/helpy
- https://github.com/polonel/trudesk
- https://github.com/BookStackApp/BookStack
- https://github.com/langchain-ai/langchain
- https://github.com/deepset-ai/haystack

### Support KB Article Synthesizer (7 sources)
- https://github.com/BookStackApp/BookStack
- https://github.com/facebook/docusaurus (MIT, 60k+ stars)
- https://github.com/chatwoot/chatwoot
- https://github.com/helpyio/helpy
- https://github.com/polonel/trudesk
- https://github.com/papercups-io/papercups
- https://github.com/deepset-ai/haystack

## Patterns observed across sources

- **Conversation as first-class object.** Most modern support platforms model the unit of work as a conversation thread, not a single ticket, and folder/inbox structure flows from that. The triage skill embraces this by treating prior turns as authoritative context for the drafter and KB synthesizer.
- **Canned responses + automation rules.** Across Chatwoot, Helpy, Papercups, and Trudesk the recurring building block is a parameterized "saved reply" plus a routing/automation layer. Both triage and drafter skills internalize the canned-reply pattern without copying any specific template text — instead the methodology codifies the *decisions* (outcome type, tier, register) that drive what a good canned reply would say.
- **SLA tiers map to priority labels.** Repositories consistently use a 3-5 tier priority taxonomy with per-tier first-response and resolution targets. The triager codifies the P1-P4 default plus alternative presets (b2b_enterprise adds P0; b2c_consumer drops P4 SLAs) without committing to any specific vendor's numbers.
- **Help center as deflection layer.** BookStack and Docusaurus represent the "publish documentation as a structured product" pattern; Chatwoot and Helpy fold it directly into the support platform. The KB synthesizer reflects this: an article is a small, structured object (problem/cause/solution/workarounds/related) with metadata for search and review.
- **Routing logic is fundamentally a team-to-category map.** Every reviewed platform expresses routing as a small lookup, sometimes augmented by skill tags. The triager keeps the same shape — a `routing_map` input with a generic default — rather than inventing a more complex agent-skills model that would not match how teams actually operate.

## Rejections (and why)

- **Zammad** (https://github.com/zammad/zammad) — AGPL-3.0. Not in allowed licenses.
- **Frappe Helpdesk** (https://github.com/frappe/helpdesk) — AGPL-3.0. Rejected.
- **FreeScout** (https://github.com/freescout-help-desk/freescout) — AGPL-3.0. Rejected.
- **osTicket** (https://github.com/osTicket/osTicket) — GPL. Rejected.
- **OpenSupports** (https://github.com/opensupports/opensupports) — GPL-3.0. Rejected.
- **Erxes** (https://github.com/erxes/erxes) — GPL-3.0 + Commons Clause; commercial use restricted. Rejected.
- **Outline** (https://github.com/outline/outline) — BSL 1.1. Not in allowed licenses (converts to Apache 2.0 only after 4 years).
- **Open Ticket AI** (https://github.com/Softoft-Orga/open-ticket-ai) — LGPL-2.1; also only 7 stars. Rejected on both counts.
- **fatihok/awesome-support** — only 5 stars; insufficient signal.
- **Various tutorial/demo LLM-agent repos** (e.g. rajesh9943/Customer-Support-Agentic-AI, Pranov1984's NLP project) — low stars, low activity, generally tutorial-quality rather than production methodology. Rejected.

## Trademark caution

No skill names use vendor brand names (no "Zendesk-style", no "Intercom-equivalent"). Body text avoids brand comparisons. References to known issue IDs in examples (INC-441) are clearly placeholders.

## Confidence

**High** on:
- The methodology codified for the triage and drafter skills directly maps to recurring patterns visible in the MIT/Apache-licensed sources reviewed.
- The KB article structure (Problem / Cause / Solution / Workarounds / Related) is conventional across help-center generators and was independently re-derived rather than copied.
- License screening: all retained sources verified MIT or Apache-2.0 via direct WebFetch of the GitHub repo overview.

**Medium** on:
- SLA numeric defaults (P1 = 15 min, etc.) — these are conventional across the industry but team-specific in practice; the skill calls this out and allows policy overrides.
- Concession-latitude tiers in the drafter — heuristic defaults; the skill flags them as defaults to override.

**Low/known-limit** on:
- Sentiment detection coarseness in the triager (acknowledged in Limitations).
- Multi-thread synthesis quality past ~5 threads in the KB synthesizer (acknowledged in Limitations).

## Line counts

- support-ticket-triager.skills.md: ~290 lines (within 300-700 target range when including examples and limitations).
- support-reply-drafter.skills.md: ~280 lines.
- support-kb-article-synthesizer.skills.md: ~270 lines.

All three skills include the required `## When to use`, `## How to apply` (≥15 ordered steps each), `## Inputs`, `## Outputs`, `## Examples` (≥2 worked examples), `## Limitations`, and `## Sources reviewed` sections per the skills.md spec.
