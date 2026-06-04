# Changelog

## 2026-05-26 — Cycle 1: Occupations + Personas

Two new product types layered on the marketplace:

- **Occupation** — a curated, graph-linked bundle of skills representing all
  methodology for a job role. First listing: **AI DevOps Engineer**
  (`skillsgit-curated/ai-devops-engineer`) — 30 cross-linked skills across 7
  domains.
- **Persona** — a composable add-on a practitioner publishes. Memory neurons
  drawn from real-world situations + decisions + outcomes, linked into a
  parent occupation. First sample: `@jane-devops-demo/incident-veteran`
  (sample data — 7 neurons).

### Highlights

- New `skills.kind` discriminator (`skill`, `occupation`, `persona`,
  `memory_neuron`) — extends the existing 456-skill library without breaking
  any existing record.
- Vault bundle delivery: stock-Obsidian-compatible `.zip` per occupation +
  per persona; composed at download time into a single per-buyer vault.
- Reference loader CLI: `uv run python -m scripts.demo_devops_agent`
  demonstrates loading a composed vault + calling Claude with neuron
  attribution.
- Capture pipeline: form → LLM extraction → PII scan → atomic publish into
  the creator's persona. Platform-key Claude (10 captures/month free for
  MVP).
- Five new Alembic migrations (0006–0010). Four new bounded contexts
  (`occupations`, `personas`, `capture`, `vault`). 800+ tests across module
  + integration suites.

### What's new in `skills.md`

Five new optional frontmatter fields (spec at
`prompts/shared/skills-md-spec.md` §Optional fields):
`kind`, `links`, `parent_occupation_id`, `neuron`, `vault_path`. All
existing files continue to validate green.

### Decisions

18 architectural decisions logged in `team/decisions.md` (ADR-001 through
ADR-018). Key choices: vault-bundle delivery only for MVP (MCP server is
Phase 2); composable persona model (separate licenses, separate payouts);
explicit `links:` frontmatter (not inferred from prose); platform-key Claude
for capture (BYOK is Phase 2).

### Frontend deferred

Per the MVP plan's "fastest path to Layer C" rule, web-creator capture UX
(T-09), persona dashboard (T-10), and marketplace occupation page (T-11)
are deferred to Cycle 2. The CLI demo proves the end-to-end value.

### Try it

```bash
docker compose -f infra/docker-compose.yml up -d
cd apps/api
uv run alembic upgrade head
uv run python -m scripts.publish_curated
uv run python -m scripts.build_devops_vault
uv run python -m scripts.build_devops_persona
uv run python -m scripts.demo_devops_agent --prompt "AWS bill is up 40% this month" --snapshot-only
# (or set ANTHROPIC_API_KEY in apps/api/.env and drop the --snapshot-only flag)
```

## [Unreleased]
- Initial monorepo scaffold (Phase 0)
