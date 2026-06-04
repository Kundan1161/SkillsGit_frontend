# Skills Git vault format

A Skills Git vault is a stock-Obsidian-compatible folder shipped as a `.zip`. It contains methodology **skills** (`kind=skill`) bundled by an **occupation** (`kind=occupation`), and optionally one or more practitioner **persona** overlays (`kind=persona`) whose **memory neurons** (`kind=memory_neuron`) link into that parent occupation. A small reference loader ships in `apps/api/scripts/demo_devops_agent.py` so you can see one end-to-end consumer, but **Skills Git does not host the runtime** — your agent (Claude Code, ChatGPT, custom) reads the vault from disk and decides what to do with it.

> **Canonical spec:** [`team/03-vault-generation.md`](../team/03-vault-generation.md).
> This file is the buyer-facing summary. Where the two disagree, the canonical spec wins.

## What's in a vault

A composed occupation + persona vault unzipped:

```
ai-devops-engineer-v1.0.0/
├── README.md                                       # human-readable overview
├── 00-index.md                                     # table of contents (by domain + persona)
├── vault.json                                      # the manifest (machine-readable index)
│
├── domains/                                        # the occupation's methodology skills
│   ├── ci-cd/
│   │   ├── ci-pipeline-architect.md
│   │   ├── gha-workflow-optimizer.md
│   │   └── ...
│   ├── observability/
│   │   ├── observability-dashboard-architect.md
│   │   └── ...
│   └── incident/
│       └── ops-incident-commander.md
│
├── personas/                                       # present once you compose ≥1 persona
│   └── jane-devops-demo/
│       └── incident-veteran/
│           ├── README.md                           # creator bio + persona description
│           ├── persona.json                        # persona-side manifest fragment
│           └── neurons/
│               ├── 2024-08-flaky-tests-after-redis-upgrade.md
│               ├── 2024-10-blue-green-rollback-at-3am.md
│               └── ...
│
└── attachments/                                    # optional, content-addressed binaries
    ├── 0a3f9c4e2d1b.png
    └── 6c8e4a2b1d0f.yaml
```

File-naming rules (enforced at build time):

- ASCII kebab-case: `[a-z0-9-]+`, no underscores, no leading/trailing hyphens.
- Max 80 chars before the `.md` extension.
- Attachments are content-addressed: `<sha256-12>.<ext>`.

## The manifest (`vault.json`)

`vault.json` at the root is the machine-readable index your agent should load first. JSON Schema lives at [`apps/api/src/vault/schema/vault-manifest-v1.json`](../apps/api/src/vault/schema/vault-manifest-v1.json). A trimmed example:

```jsonc
{
  "$schema": "https://skillsgit.com/schema/vault-manifest-v1.json",
  "schema_version": 1,
  "vault_id": "01HX...",
  "occupation": {
    "skill_id": "01HX...",
    "name": "AI DevOps Engineer",
    "slug": "ai-devops-engineer",
    "creator_handle": "skillsgit-curated",
    "version": "1.0.0",
    "content_hash": "abc123...",
    "domains": ["ci-cd", "observability", "incident", "iac",
                "security", "cost", "platform"]
  },
  "personas": [
    {
      "skill_id": "01HX...",
      "name": "Incident Veteran (sample data)",
      "slug": "incident-veteran",
      "creator_handle": "jane-devops-demo",
      "version": "1.0.0",
      "content_hash": "def456...",
      "neuron_count": 7,
      "parent_occupation_id": "01HX..."
    }
  ],
  "files": [
    {
      "vault_path": "domains/ci-cd/ci-pipeline-architect.md",
      "skill_id": "01HX...",
      "version": "1.0.0",
      "kind": "skill",
      "creator_handle": "skillsgit-curated",
      "content_hash": "...",
      "tags": ["ci-cd", "github-actions"],
      "links": [
        {"target": "domains/observability/observability-dashboard-architect",
         "relation": "see-also", "resolved": true}
      ],
      "links_resolved": true
    },
    {
      "vault_path": "personas/jane-devops-demo/incident-veteran/neurons/2024-08-flaky-tests-after-redis-upgrade.md",
      "skill_id": "01HX...",
      "version": "1.0.0",
      "kind": "memory_neuron",
      "creator_handle": "jane-devops-demo",
      "content_hash": "...",
      "tags": ["sample-data", "ci", "redis", "flaky-tests"],
      "links": [
        {"target": "domains/ci-cd/ci-pipeline-architect",
         "relation": "applies", "resolved": true}
      ],
      "links_resolved": true,
      "neuron": {
        "situation": "...",
        "decision": "...",
        "outcome": "...",
        "recorded_at": "2024-08-22",
        "confidence": 0.9
      }
    }
  ],
  "attribution_index": {
    "01HX-skill-id-1": "domains/ci-cd/ci-pipeline-architect.md",
    "01HX-skill-id-2": "personas/jane-devops-demo/incident-veteran/neurons/2024-08-flaky-tests-after-redis-upgrade.md"
  },
  "build": {
    "occupation_build_id": "01HX...",
    "occupation_build_hash": "...",
    "persona_build_ids": ["01HX..."],
    "persona_build_hashes": ["..."],
    "composed_hash": "ghi789...",
    "built_at": "2026-05-26T18:30:00Z",
    "composed_at": "2026-05-26T18:30:42Z"
  },
  "warnings": []
}
```

Key fields your agent will care about:

- **`files[]`** — every `.md` file in the vault with `vault_path`, `kind`, `creator_handle`, `version`, `content_hash`, `tags`, resolved `links`. `kind=memory_neuron` entries also carry a structured `neuron` block mirrored from frontmatter for fast scanning.
- **`attribution_index{}`** — `skill_id → vault_path` lookup. Use this when an LLM reports a `skill_id` and you want the human-readable file path back.
- **`personas[]`** — one entry per overlaid persona. `neuron_count` is the size of that persona's contribution; `parent_occupation_id` is the occupation it overlays.
- **`warnings[]`** — soft warnings (unresolved cross-links, missing attachments). Non-fatal but worth surfacing to your agent for trust — a vault with zero warnings is fully self-consistent.

## Attribution comments

Every `.md` the builder emits carries a trailing HTML comment as a belt-and-suspenders citation token for tools that load files one at a time (without reading `vault.json`):

```html
<!-- skg-attribution:
  vault_path: "domains/ci-cd/ci-pipeline-architect.md"
  skill_id: "01HX..."
  version: "1.0.0"
  kind: "skill"
  creator_handle: "skillsgit-curated"
  content_hash: "..."
  built_at: "2026-05-26T18:30:00Z"
-->
```

Why it exists: an agent can quote the `vault_path` and `version` in its answer ("I consulted `domains/ci-cd/ci-pipeline-architect.md` v1.0.0") without keeping `vault.json` in context. The comment is invisible to markdown renderers and safe for LLMs — HTML comments inside markdown are no-ops, and the structured `key: value` lines aid your audit logs without confusing the model.

## Wiki-links

References between files are emitted as Obsidian `[[vault_path]]` wiki-links. They are **explicit** — every link is sourced from the `links:` frontmatter on the originating file, never inferred from prose. The builder appends a stable `## Linked notes` section to each file's body so Obsidian's graph view picks them up:

```markdown
## Linked notes

- [[domains/incident/ops-incident-commander]] — applies
- [[domains/observability/observability-dashboard-architect]] — see-also
```

`relation` values are `applies`, `extends`, `contradicts`, `see-also`, `recorded-instance-of`. Authors may also use inline `[[wiki-links]]` in body prose for readability — those render in Obsidian but are not extracted into `vault.json`. If you want a complete graph, walk `files[].links[]` from the manifest.

Open `Ctrl-G` (`Cmd-G` on macOS) in Obsidian to see the graph view rendered from these links. A vault of 30 occupation skills + 7 neurons is interactive and instant.

## Watermarks

Every `.md` file in a downloaded vault also carries a per-buyer watermark line at the bottom:

```html
<!-- license:8f3a1c... buyer:9b4d2e... ts:2026-05-26T18:30:42Z -->
```

What it does:

- Identifies the source of a leaked file. The `license:` and `buyer:` values are HMAC-hashed (not raw IDs), so the watermark doesn't expose customer data.
- Safe to feed to an LLM — HTML comments are markdown no-ops, and the model has no reason to surface them in output.
- Per-buyer. Two different buyers downloading the same composed bundle get bytewise-identical files **except** for the watermark and the watermark timestamp. That property makes leak attribution trivial and CI snapshot diffs predictable.

The attribution comment (section above) sits between the body and the watermark. Order in every delivered file: frontmatter → body → `## Linked notes` → `<!-- skg-attribution: ... -->` → `<!-- license: ... -->`.

## A reference loader (Python)

The canonical reference loader is [`apps/api/scripts/demo_devops_agent.py`](../apps/api/scripts/demo_devops_agent.py). A minimal version showing the pattern:

```python
import io
import json
import re
import zipfile
from pathlib import Path

_CONSULTED_RE = re.compile(r"```consulted\s*\n(?P<body>.*?)\n```", re.DOTALL)


def load_vault(zip_path: Path) -> tuple[dict, dict[str, str]]:
    """Open the vault zip, return (manifest, body_by_vault_path)."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        manifest = json.loads(zf.read("vault.json").decode("utf-8"))
        bodies = {
            entry["vault_path"]: zf.read(entry["vault_path"]).decode("utf-8")
            for entry in manifest["files"]
        }
    return manifest, bodies


def build_system_prompt(manifest: dict, bodies: dict[str, str]) -> str:
    """One short summary per file the LLM can route from."""
    lines = ["You may consult the following files. Cite each you use:"]
    for entry in sorted(manifest["files"], key=lambda f: f["vault_path"]):
        path = entry["vault_path"]
        body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", bodies[path],
                      flags=re.DOTALL)
        summary = re.sub(r"\s+", " ", body).strip()[:200]
        lines.append(f"- ({entry['kind']}) {path}: {summary}")
    lines.append(
        "\nEnd your reply with a ```consulted block listing one "
        "vault_path per line for every file you actually used."
    )
    return "\n".join(lines)


def parse_consulted(reply: str) -> list[str]:
    """Extract the paths the LLM said it consulted."""
    m = _CONSULTED_RE.search(reply)
    if not m:
        return []
    return [line.strip().lstrip("- ") for line in m.group("body").splitlines()
            if line.strip()]


def cite(manifest: dict, vault_path: str) -> str:
    """Render a citation string from the manifest's file entry."""
    entry = next(f for f in manifest["files"] if f["vault_path"] == vault_path)
    return f"{vault_path} ({entry['creator_handle']}, v{entry['version']}, {entry['kind']})"
```

The full reference adds: license-and-buyer bootstrap, a real Anthropic SDK call, table-rendered output, and a `--snapshot-only` mode for CI. Run it with:

```bash
uv run python -m scripts.demo_devops_agent \
    --prompt "my CI just started failing intermittently"
```

Pass `--snapshot-only` to skip the LLM call entirely and print the composed-vault listing instead.

## Versions and updates

The current manifest is `vault-manifest-v1.json` (`schema_version: 1`). Schema evolution policy:

- **v1.x — additive only.** New optional fields are non-breaking. Existing consumers continue to load v1.x vaults emitted by any newer build.
- **v2+ — breaking changes.** Anything that adds a required field or changes a value's semantics ships under a new `$schema` URL. We'll publish v1 → v2 migration notes in the changelog when that happens.

Buyers can pin a specific vault build by its `build.occupation_build_hash` + `build.persona_build_hashes` — these are stable per `(skill_id, version)`. Re-downloading a vault whose source hasn't changed produces an identical archive (modulo the per-buyer watermark and `built_at` timestamp). See [`team/decisions.md`](../team/decisions.md) ADR-006, ADR-010, ADR-013 for the why.

## What this is NOT

- **Not a hosted runtime.** Skills Git ships the vault file; your agent runs it. The reference loader is a demo, not infrastructure.
- **Not a streaming API.** Updates are pulled. A buyer's agent re-downloads to receive a new build; the library page surfaces a "new build available" badge.
- **Not Obsidian-specific.** Any tool that can read markdown + JSON works. Obsidian compatibility is a feature (graph view, search, link previews) — not a dependency. We ship no plugins and no `.obsidian/` config beyond an optional `graph.json` color-by-tag preset for the demo.
