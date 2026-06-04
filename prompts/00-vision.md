# 00 — Vision

**Phase:** 0 (shared context)
**Depends on:** none
**Parallel-safe with:** all
**Status:** ready

> Every agent working in this repo should read this file first. It defines what we're building, who it's for, and the non-negotiables.

---

## The product in one sentence

A marketplace where professionals across industries package their expertise as reusable AI **skills** (skills.md files) — and a visual builder that lets them author those skills without writing code.

## The two halves

### 1. Marketplace (build first)

A two-sided platform: **creators** publish skills, **buyers** discover, license, and integrate them into their own agents.

- Buyers browse by category (finance, design, marketing, data, legal, ops, …), preview skills in a sandbox, then license them via one-time purchase, monthly subscription, or freemium.
- Creators see sales analytics, manage versions, push updates to existing buyers, and get paid via Stripe Connect.
- Platform takes a revenue share on every transaction.

### 2. Skill Creator engine (build second)

A visual node-based builder where a non-technical professional can:

- Capture their **decision-making process** as a graph of modular nodes (context → decision → parameter → output).
- **Import** existing work from Claude Code projects, OpenAI Custom GPTs, OpenAI Assistants, or Codex projects, and have it parsed into a starting graph.
- Specify **AI runtime requirements** (which model is required, which tools, minimum context window).
- Compile the graph into a valid `skills.md` file ready to publish to the marketplace.
- Test the skill against the target model(s) in a sandbox before publishing.
- Push updates to existing buyers without breaking semver guarantees.

## Target users

**Creators** — professionals who own a repeatable methodology and want to monetize it:
- Web/UI designers with a critique framework
- Data architects with a schema-design playbook
- Financial analysts with a DCF or LBO methodology
- Marketers with a campaign-planning system
- SEO strategists, ops leads, compliance officers, legal-ops, etc.

**Buyers** — individuals or teams who want to plug expert methodology into their AI agents without learning to prompt-engineer it themselves.

> **Critical:** creators are largely **non-technical**. The visual builder must be usable by someone who has never written code. The marketplace must be usable by someone who has never installed a CLI.

## Non-negotiables

1. **skills.md is the canonical artifact.** Every flow — authoring, listing, licensing, delivery, updates — operates on this file. The format is defined in `shared/skills-md-spec.md` and must not diverge between marketplace and creator.

2. **Trust is the moat.** Buyers must believe a skill does what it claims. We invest in: sandbox previews, verified-creator badges, reviews & ratings, content moderation, automated quality checks at publish time.

3. **Updates are first-class.** Skills evolve. Buyers must be notified of new versions and able to opt-in (or auto-receive) updates within their license tier. Creators must be able to publish patches without re-pricing or re-licensing.

4. **Multi-model from day one.** A skill declares which AI model(s) it targets (Claude, GPT, Gemini, open-source) and the marketplace surfaces this clearly. We do not lock skills to one vendor.

5. **Payouts are correct.** Stripe Connect, transparent fee math, audit trail per transaction. Creators always know what they earned and when they get paid.

## What we're explicitly **not** building (yet)

- A general-purpose agent runtime. Buyers run skills inside their own agents (Claude Code, ChatGPT, custom). We deliver the file; they wire it up. (Optional integrations come later.)
- A code editor. The visual builder produces skills.md; it is not an IDE.
- An LLM router or inference service. We don't host model calls — sandbox previews proxy to creator-owned API keys or a metered platform key.
- Real-time multi-user co-editing of skills. Single-author edits with version history is enough for v1.

## North-star metrics (for context, not to optimize prematurely)

- Time-to-first-listing for a new creator: **< 30 minutes** from sign-up.
- Buyer "first useful skill imported into my agent": **< 5 minutes** from purchase.
- Creator gross earnings retention (revenue share net of refunds): **target 75%+** going to creator.
- Update adoption rate among active licensees: **> 60% within 7 days** of release.
