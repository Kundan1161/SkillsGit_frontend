# 07 — Layer-C demo CLI

Diagrams of the `scripts/demo_devops_agent.py` reference loader — the
"AI DevOps Engineer" Cycle-1 demo. The CLI takes a DevOps question,
composes the AI-DevOps-Engineer occupation + the `incident-veteran`
persona for a demo buyer, opens the composed vault, sends Claude a
neuron index + the prompt, and renders the answer with per-neuron
attribution.

Per **ADR-018**, this CLI is a REFERENCE LOADER — not a hosted
runtime. Skills Git ships the vault; the buyer's own agent (Claude
Code, ChatGPT, custom) runs it. The demo uses Claude directly for
demo's sake; production buyers BYOK their own model.

Source: `apps/api/scripts/demo_devops_agent.py` read directly — the
diagrams describe what the script actually does, including the
`--snapshot-only` short-circuit used by CI and the per-line attribution
extraction.

## Files

### [`demo-cli-sequence.drawio`](demo-cli-sequence.drawio) — end-to-end flow

Sequence diagram covering all six phases: argparse → skill resolution
(via `creator_handle/slug`) → idempotent demo buyer + free `grant`
licenses → `compose_for_license` → S3 fetch of the composed zip →
`vault.json` parse into a neuron lookup → branch (snapshot-only vs
live LLM). The live branch builds a system message with one
summarised line per neuron, calls Claude via the shared
`core/anthropic.py` client, parses the consulted block, and renders
the answer + attribution table. Exit codes: 0 success, 2 missing
prereqs (skill not found, no API key), 3 LLM failure.

### [`attribution-extraction.drawio`](attribution-extraction.drawio) — consulted-block parse

How the CLI gets per-neuron attribution out of Claude's free-form
response. The system prompt's contract instructs Claude to append a
fenced ` ```consulted ... ``` ` block listing 1-8 vault paths.
`_parse_consulted_block` regex-extracts the block, normalises each
line (strip leading dash, surrounding quotes/backticks, whitespace),
intersects against the composed vault's manifest lookup, and renders
a table of `(vault_path, kind, creator, version)`. Unknown paths
(hallucinations) are surfaced as warnings but never attributed —
the CLI refuses to attribute work to files the buyer doesn't own.

### [`snapshot-mode-flow.drawio`](snapshot-mode-flow.drawio) — `--snapshot-only`

What changes when `--snapshot-only` is supplied: argparse relaxes the
`--prompt` requirement; the LLM call + prompt-build + attribution
parse are all skipped; `_print_snapshot_listing` prints the full
alphabetical file listing + manifest warning count. CI's
`team-smoke.yml` workflow runs in this mode with `ANTHROPIC_API_KEY=""`
so the snapshot test never hits the network. Important: the compose
step still runs (DB writes, S3 reads, watermark, etc.) so structural
drift in the compose path is caught by the snapshot diff, not just
seed-data drift.

## Snapshot mode vs live mode — quick reference

| | snapshot-only | live |
|---|---|---|
| `--prompt` / `--prompt-id` required | no | yes (or `--snapshot-only`) |
| `ANTHROPIC_API_KEY` required | no | yes |
| Resolve skills + buyer + licenses | yes | yes |
| Run `compose_for_license` | yes | yes |
| Parse `vault.json` lookup | yes | yes |
| Build system message (neuron index) | no | yes |
| Call Anthropic API | no | yes |
| Parse consulted block | no | yes |
| Render attribution table | no | yes |
| Print full file listing | yes | no |
| Used by CI (`team-smoke.yml`) | yes | no |
| Exit codes | 0, 2 | 0, 2, 3 |

## ADR-018 — reference loader, not runtime

The CLI banner prints this on every run:

```
== REFERENCE LOADER == (not a hosted runtime)
Skills Git ships the vault. Your agent (Claude Code, ChatGPT,
custom) runs it.
This CLI is a sample integration that calls Claude directly for
the demo.
```

The intent: prevent anyone reading the demo from concluding "Skills
Git is a hosted agent platform". It is a marketplace that ships
agent-consumable vaults; the agent runtime stays with the buyer.

## How to view

Every file in this folder is a `.drawio` file. Open it in the draw.io
desktop app or at [app.diagrams.net](https://app.diagrams.net), or
render it inline in VS Code with the
[Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio)
extension. See [`docs/diagrams/README.md`](../README.md#how-to-view-these-diagrams)
for the full guide and the two flavours of `.drawio` in this repo
(native mxgraph vs Mermaid-embedded).

## Source pointers

| Topic | File |
|---|---|
| CLI entry point | `apps/api/scripts/demo_devops_agent.py` |
| Banner + ADR-018 framing | `apps/api/scripts/demo_devops_agent.py:_print_banner` |
| argparse + persona normalisation | `apps/api/scripts/demo_devops_agent.py:_parse_args` + `_normalise_personas` |
| Skill resolution by handle/slug | `apps/api/scripts/demo_devops_agent.py:_resolve_skill_by_handle_slug` |
| Idempotent buyer + free licenses | `apps/api/scripts/demo_devops_agent.py:_ensure_demo_buyer` + `_ensure_free_license` |
| Compose + load vault into memory | `apps/api/scripts/demo_devops_agent.py:_compose_and_load` |
| Vault.json → neuron lookup | `apps/api/scripts/demo_devops_agent.py:_load_vault_lookup` |
| System message + neuron index | `apps/api/scripts/demo_devops_agent.py:_build_system_message` + `_SYSTEM_PREAMBLE` |
| Claude call + result dataclass | `apps/api/scripts/demo_devops_agent.py:_call_claude` + `AgentReply` |
| Consulted-block regex | `apps/api/scripts/demo_devops_agent.py:_CONSULTED_FENCE_RE` + `_parse_consulted_block` |
| Snapshot listing | `apps/api/scripts/demo_devops_agent.py:_print_snapshot_listing` |
| Stock prompts (`--prompt-id`) | `apps/api/scripts/seed_data/demo/prompts.yaml` |
| Shared Anthropic client | `apps/api/src/core/anthropic.py` |
| CI consumer | `.github/workflows/team-smoke.yml` |
| Snapshot test | `apps/api/tests/integration/test_demo_cli_snapshot.py` |
| `_parse_consulted_block` unit tests | `apps/api/scripts/tests/test_parse_consulted_block.py` |
| ADR-018 (reference loader vs runtime) | `team/decisions.md` |
