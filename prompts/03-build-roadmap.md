# 03 — Build Roadmap

**Phase:** 0 (shared context)
**Depends on:** `00-vision.md`, `01-tech-stack-and-repo.md`, `02-data-model-core.md`
**Parallel-safe with:** all
**Status:** ready

> Phasing exists so we ship a working marketplace before we ship an authoring tool. **No skill-creator code merges before Phase 2 is done.** Exception: `shared/skills-md-spec.md` is needed by both halves and is part of Phase 1.

---

## Phase 0 — Foundation (single agent, sequential)

**Goal:** the repo runs, types check, CI is green, the data model exists.

Prompts in this phase:
- `01-tech-stack-and-repo.md` (scaffold the monorepo)
- `02-data-model-core.md` (SQLAlchemy + Alembic + Pydantic + codegen)
- `shared/auth.md` (sign-up, sign-in, sessions, role bootstrap)
- `shared/api-conventions.md` (error format, pagination, OpenAPI)
- `shared/design-system.md` (Tailwind, shadcn, primitives)
- `shared/skills-md-spec.md` (the file format)

**Exit criteria:**
- A user can register, sign in, sign out.
- An admin can create a creator profile from a script.
- The skills.md spec validator parses a hand-written example.

---

## Phase 1 — Marketplace MVP (parallelizable across ~3 agents)

**Goal:** a creator can manually publish a skills.md file via the admin/CLI; a buyer can browse, purchase one-time, and download.

Prompts in this phase:
- `marketplace/00-overview.md`
- `marketplace/01-discovery.md` — homepage, browse by category, search, filters
- `marketplace/02-skill-detail.md` — listing page, screenshots, version history, reviews
- `marketplace/03-pricing-and-checkout.md` — **one-time only in this phase**; subscription deferred
- `marketplace/04-licensing-and-delivery.md` — license issuance, signed download URLs

**Suggested parallel split:**
- Agent A: discovery + skill detail (frontend-heavy)
- Agent B: pricing + checkout + Stripe Connect onboarding
- Agent C: licensing + delivery + audit log

**Exit criteria:**
- A buyer can find a skill, buy it for $X one-time, and download the skills.md file.
- The creator sees the sale in `audit_log` and gets a Stripe transfer queued.
- Refunds via Stripe webhook revoke the license.

---

## Phase 2 — Trust, monetization, and updates (parallel, ~3 agents)

**Goal:** the marketplace is *trustworthy* and the *full* pricing model is live.

Prompts in this phase:
- `marketplace/03-pricing-and-checkout.md` — extend with **subscriptions** and **freemium**
- `marketplace/05-trust-and-quality.md` — reviews, ratings, moderation, sandbox preview
- `marketplace/06-versioning-and-updates.md` — semver enforcement, update notifications
- `marketplace/07-creator-dashboard.md` — sales analytics, payouts UI

**Suggested parallel split:**
- Agent A: subscriptions + freemium pricing
- Agent B: reviews + moderation + sandbox preview
- Agent C: creator dashboard + versioning UX

**Exit criteria:**
- A buyer can subscribe monthly with support tier; cancel; auto-renew.
- A buyer who owns a one-time license sees a "v2.0 available" banner and can choose to upgrade.
- A creator sees lifetime earnings, monthly subscription MRR, and pending payout.
- All publish events run through automated quality checks (schema validation, content hash, malware scan placeholder).

---

## Phase 3 — Skill Creator engine (parallel, ~2 agents)

**Goal:** a non-technical creator can author a skills.md file visually without writing markdown.

Prompts in this phase:
- `skill-creator/00-overview.md`
- `skill-creator/01-visual-builder.md` — React Flow canvas, node types, graph → markdown compiler
- `skill-creator/03-skill-config.md` — metadata form (name, pricing, AI requirements, categories)
- `skill-creator/04-test-and-preview.md` — sandbox runtime, model picker, preview pane

**Suggested parallel split:**
- Agent A: canvas + node types + compilation
- Agent B: config form + sandbox runtime

**Exit criteria:**
- A creator builds a 5-node skill (context → 2 decisions → output) on the canvas.
- The compiled skills.md passes validation against `shared/skills-md-spec.md`.
- The creator runs the skill against Claude in the sandbox and sees the output.

---

## Phase 4 — Import + publishing loop (parallel, ~2 agents)

**Goal:** creators bring in work from existing AI platforms; published skills go straight to the marketplace.

Prompts in this phase:
- `skill-creator/02-import-from-projects.md` — Claude Code SKILL.md, OpenAI Custom GPT, OpenAI Assistant, Codex
- `skill-creator/05-publish-to-marketplace.md` — push from creator app → draft listing → pending review → live

**Exit criteria:**
- A creator pastes their Claude Code project URL or uploads a GPT export, sees an initial graph populated.
- A creator clicks "Publish" and within 60 seconds the skill is in `pending_review`.
- Admin approval flips it to `published` and it appears in discovery.

---

## Phase 5 — Updates ecosystem (single agent, end-to-end polish)

**Goal:** the loop of creator-pushes-update → buyer-notified → buyer-adopts is delightful.

Touches files across both apps; not a new prompt — extends `marketplace/06-versioning-and-updates.md` and `skill-creator/05-publish-to-marketplace.md`.

**Exit criteria:**
- A creator publishes 1.2.0; all active subscribers see a "what's new" prompt next time they open the buyer dashboard.
- One-time owners of 1.x get a banner; major version (2.0.0) triggers an upgrade-purchase flow.
- Creators can deprecate or yank a version with a typed reason that buyers see.

---

## Phasing rules

1. **No prompt jumps phases unless the previous phase has met its exit criteria.** If an agent thinks a prompt is misclassified, raise it in the prompt's header — don't silently re-order.
2. **Foundation > experience.** Until Phase 2 ships, the marketplace UI can look rough. Visual polish is a Phase 2 line item, not a Phase 1 blocker.
3. **No new tables in later phases without updating `02-data-model-core.md`.** Phase-specific tables are fine in their own prompt files.
4. **Every phase ends with a written changelog entry** in `docs/changelog.md` (created in Phase 0).
