# Prompts — Skills Marketplace & Creator

This folder contains **agent-executable prompts** for building a two-sided platform:

1. **Marketplace** — where professionals buy, sell, and update AI "skills" (skills.md files).
2. **Skill Creator** — a visual node-based builder for producing skills.md files, with imports from existing AI projects (Claude Code, OpenAI Assistants, etc.).

**Build order: marketplace first, then creator.** The marketplace must be able to host, deliver, and meter access to skills before we ship the authoring tool — otherwise we have inventory with nowhere to sell it.

---

## How to use these prompts

Each `.md` file in this folder is a **self-contained brief** for an AI coding agent. An agent should be able to pick up any file labeled "ready" and execute it without reading the rest of this folder beyond its declared dependencies.

### Standard file header

Every prompt starts with:

```
**Phase:** 1 | 2 | 3
**Depends on:** [list of prompt files this needs first]
**Parallel-safe with:** [prompts that can run alongside this one]
**Status:** ready | in-progress | done | blocked
**Owner:** [agent id or empty]
```

### Reading order for a new agent

1. `00-vision.md` — the product
2. `01-tech-stack-and-repo.md` — the stack and repo layout
3. `02-data-model-core.md` — entities shared across the system
4. `03-build-roadmap.md` — phasing and which prompts belong to which phase
5. `shared/skills-md-spec.md` — the file format that ties the whole system together
6. The specific prompt assigned to the agent

### Updating status

When an agent picks up a prompt, it should:
1. Set `Status: in-progress` and `Owner: <agent-id>` in the file header.
2. Commit incremental progress with clear messages.
3. Set `Status: done` only when acceptance criteria are met.

---

## Folder layout

```
prompts/
├── README.md                     ← you are here
├── 00-vision.md                  shared context: what we're building and why
├── 01-tech-stack-and-repo.md     FastAPI + Next.js + Postgres + Stripe, repo layout
├── 02-data-model-core.md         shared entities (User, Skill, Version, etc.)
├── 03-build-roadmap.md           phasing and prompt-to-phase mapping
│
├── shared/                       cross-cutting concerns referenced by both apps
│   ├── auth.md                   user auth, sessions, API tokens
│   ├── api-conventions.md        REST conventions, error format, pagination
│   ├── design-system.md          Tailwind + shadcn/ui, tokens, primitives
│   └── skills-md-spec.md         THE skills.md file format
│
├── marketplace/                  Phase 1–2: ship this first
│   ├── 00-overview.md
│   ├── 01-discovery.md           browse, search, categories, filters
│   ├── 02-skill-detail.md        listing page, preview, version history
│   ├── 03-pricing-and-checkout.md   tiers, Stripe Connect, freemium, subscriptions
│   ├── 04-licensing-and-delivery.md how buyers receive skill files
│   ├── 05-trust-and-quality.md   reviews, ratings, sandbox preview, moderation
│   ├── 06-versioning-and-updates.md  semver, notifications, auto-update
│   └── 07-creator-dashboard.md   earnings, sales analytics, payout
│
└── skill-creator/                Phase 3–4: ship after marketplace MVP
    ├── 00-overview.md
    ├── 01-visual-builder.md      React Flow canvas + node compilation
    ├── 02-import-from-projects.md  Claude Code, GPTs, Assistants, Codex
    ├── 03-skill-config.md        model requirements, metadata, validation
    ├── 04-test-and-preview.md    sandbox runtime against multiple models
    └── 05-publish-to-marketplace.md push from creator → listing
```

---

## Parallelism guide

These prompts are designed so up to **6 agents** can work concurrently after the foundation is laid:

- **Foundation wave** (sequential, single agent): `00–03` + `shared/*`. ~1–2 days.
- **Marketplace wave** (parallel, 3–4 agents): everything under `marketplace/`.
- **Creator wave** (parallel, 2–3 agents): everything under `skill-creator/`.

Each prompt declares its `Parallel-safe with:` list so agents don't step on each other.

---

## Quality bar

- All code is **type-checked** (mypy on backend, strict TS on frontend).
- All API endpoints have **OpenAPI schemas** and integration tests.
- All user-facing features ship with **at least one happy-path E2E test** (Playwright).
- No agent ships UI without **manually exercising the feature in a browser** first.
