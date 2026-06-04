# skillsgit

A two-sided marketplace for AI **skills** — `skills.md` files that package professional methodology into something an AI agent can use.

> Currently in **Phase 0** (foundation / scaffolding). See [`prompts/03-build-roadmap.md`](prompts/03-build-roadmap.md) for the full phasing.

## Quickstart

Prereqs: Node 22+, pnpm 9+, Python 3.12+, Docker.

```bash
# 1. Start local infra (postgres, redis, minio, mailhog)
docker compose -f infra/docker-compose.yml up -d

# 2. Install JS workspace deps
pnpm install

# 3. Run all three apps in parallel
#    api          :8000
#    marketplace  :3000
#    creator      :3001
pnpm dev
```

Useful URLs once running:

- MinIO console: <http://localhost:9001>
- Mailhog UI:    <http://localhost:8025>
- API docs:      <http://localhost:8000/docs>

## Repo layout

```
skillsgit/
├── apps/
│   ├── api/                 FastAPI backend (single source of truth)
│   ├── web-marketplace/     Next.js — public marketplace + buyer UX
│   └── web-creator/         Next.js — visual builder for creators
│
├── packages/
│   ├── skills-schema/       Zod schemas + TS types for skills.md frontmatter
│   ├── api-client/          Typed fetch client generated from FastAPI OpenAPI
│   └── ui/                  Shared shadcn/ui primitives + design tokens
│
├── infra/
│   ├── docker-compose.yml   Local dev infra
│   └── seed/                Fixture data
│
├── prompts/                 Agent-facing build specs (canonical)
├── docs/                    Human-readable derived docs (changelog, etc.)
├── .github/workflows/       CI: lint, typecheck, test, build
├── pnpm-workspace.yaml
├── tsconfig.base.json
└── package.json             Workspace root
```

## Where to find things

- **Build specs (canonical):** [`prompts/`](prompts/) — start with `00-vision.md` and `01-tech-stack-and-repo.md`.
- **Human-readable docs:** [`docs/`](docs/) — changelog, API style pointer.
- **Design system:** [`prompts/shared/design-system.md`](prompts/shared/design-system.md).
- **API conventions:** [`prompts/shared/api-conventions.md`](prompts/shared/api-conventions.md).
- **skills.md spec:** [`prompts/shared/skills-md-spec.md`](prompts/shared/skills-md-spec.md).

## Common scripts

| Script | What it does |
| ------ | ------------ |
| `pnpm dev`          | Run api + marketplace + creator concurrently |
| `pnpm build`        | Build every workspace package/app |
| `pnpm lint`         | Lint every workspace |
| `pnpm typecheck`    | TypeScript check every workspace |
| `pnpm test`         | Run all workspace tests |
| `pnpm format`       | Prettier write everything |
| `pnpm format:check` | Prettier check (CI) |
| `pnpm codegen`      | Regenerate `@skillsgit/api-client` from the live API (placeholder in Phase 0) |
