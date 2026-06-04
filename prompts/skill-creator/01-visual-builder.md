# skill-creator — 01 Visual Builder

**Phase:** 3
**Depends on:** `skill-creator/00-overview.md`, `shared/skills-md-spec.md`, `shared/design-system.md`
**Parallel-safe with:** `02-import-from-projects.md`, `03-skill-config.md`, `04-test-and-preview.md`, `05-publish-to-marketplace.md`
**Status:** ready
**Owner:** _empty_

> The canvas is the product. Every other surface refers back to it. Build it once, build it right.

---

## Scope

- React Flow canvas (`/skills/{id}/builder`).
- Node palette (left rail) and inspector (right rail).
- Node type definitions and their data shapes.
- Edge types and validation.
- Graph → skills.md compiler.
- Skills.md → graph parser (best-effort, used on import and on re-open).
- Autosave & snapshots.

**Not** in scope: AI requirement metadata (lives in `03-skill-config.md`), sandbox runs (`04`), publish wizard (`05`).

---

## Tech

- `@xyflow/react` (React Flow v12). Use it strictly client-side (`"use client"`).
- Zustand for canvas state (`useBuilderStore`). React Flow's internal state is separate; we mirror to Zustand only what we need to compile/save.
- TanStack Query for autosave mutations (debounced).
- `nanoid` for in-graph node IDs (separate from DB IDs).
- `unified` + `remark` for compilation/parsing.

---

## Canvas layout

```
┌──────────┬──────────────────────────────────────────────┬──────────┐
│ Palette  │                                              │ Inspector│
│  (left)  │              ReactFlow canvas                │  (right) │
│          │                                              │          │
│ • Context│                                              │ Selected:│
│ • Decision                                              │  Decision│
│ • Param  │             [nodes & edges]                   │          │
│ • Action │                                              │  Title:..│
│ • Output │                                              │  Prompt:.│
│ • Note   │                                              │          │
│          │                                              │          │
│          │  [zoom] [fit] [snap] [validate] [compile]    │          │
└──────────┴──────────────────────────────────────────────┴──────────┘
```

- Top bar: skill name (editable inline), version target ("1.3.0"), "Open config", "Preview", "Run in sandbox", "Publish".
- Bottom bar: validation status pill (`✓ Valid` / `! 3 issues`), last-saved indicator.

---

## Node types

Each node has a stable `kind` field and a typed `data` payload.

```ts
type BaseNode = {
  id: string;          // nanoid
  kind: NodeKind;
  position: { x: number; y: number };
  data: NodeData;      // varies by kind
};

type NodeKind =
  | "context"
  | "decision"
  | "parameter"
  | "action"
  | "output"
  | "example"
  | "note";
```

### `context` — "Who you are / when to use"

Used to render the `## When to use` section of skills.md. Typically one per skill.

```ts
type ContextData = {
  title: string;          // e.g., "When to use this skill"
  description: string;    // markdown; rendered into the skill body
  trigger_keywords: string[];  // surfaces into frontmatter.trigger_keywords
  example_invocations: string[]; // surfaces into frontmatter.example_invocations
};
```

### `decision` — "If/then logic"

A branching point. Compiles into a step in `## How to apply` with sub-bullets.

```ts
type DecisionData = {
  title: string;
  question: string;       // "Is the company public?"
  branches: Array<{
    label: string;        // "Yes" / "No" / "Pre-revenue"
    instruction: string;  // markdown
  }>;
};
```

Edges from a decision node carry a `branchLabel` to denote which path they belong to.

### `parameter` — "Input the agent should collect"

Compiles into `inputs[]` frontmatter and an `## Inputs` body section.

```ts
type ParameterData = {
  name: string;           // slug
  label: string;          // human label
  type: "text" | "file" | "url" | "json" | "number" | "choice";
  required: boolean;
  description: string;
  choices?: string[];     // when type=choice
};
```

### `action` — "Do this step"

A workhorse step. Compiles into a numbered item in `## How to apply`.

```ts
type ActionData = {
  title: string;
  instruction: string;    // markdown
  uses_tool?: string;     // optional reference to a tool listed in frontmatter.tools_required
};
```

### `output` — "What the agent produces"

Compiles into `outputs[]` frontmatter and `## Outputs` body section. Typically one per skill, but multi-output is supported.

```ts
type OutputData = {
  name: string;
  type: "text" | "markdown" | "json" | "file";
  description: string;
  schema?: string;        // JSON schema string, if type=json or file
};
```

### `example` — "Worked example"

Compiles into `## Examples` body. Multiple allowed.

```ts
type ExampleData = {
  title: string;
  input_summary: string;
  output_summary: string;
  full_example_md?: string;  // optional fuller worked example
};
```

### `note` — "Notes-to-self, not exported"

Authoring-only. Never appears in the compiled output. Grey, dashed border.

```ts
type NoteData = { text: string; };
```

---

## Edges

Edges are typed:

```ts
type Edge = {
  id: string;
  source: string;
  target: string;
  type: "default" | "branch";
  data?: { branchLabel?: string; };
};
```

Rules (enforced in `addEdge` reducer; surface as warnings, not hard blocks while drafting):
- Context node has no incoming edges.
- Output node has no outgoing edges (terminal).
- Parameter nodes are connected to action/decision nodes that consume them — but the graph is *not* a strict execution graph; edges are guides for compilation order.
- A decision node's outgoing edges should be labeled with a branch (warn if unlabeled).
- No cycles. Warn but don't hard-block; compilation linearizes via topological sort with cycle-breaking on the most recently-added edge.

---

## Palette (left rail)

- Draggable chips for each node type.
- A "Templates" sub-section beneath the chips: pre-built sub-graphs (e.g., "3-step DCF flow", "Visual critique rubric"). Drops in 5–10 connected nodes at once. Stored in `apps/web-creator/lib/builder/templates.ts`.

## Inspector (right rail)

Renders a form for the selected node's `data`. Uses RHF + Zod with a schema per node kind. Mounts/unmounts on selection change.

Multi-select: shows a "Multiple nodes selected" stub with bulk actions (delete, copy).

No selection: shows "Skill outline" — a collapsible tree of all nodes for navigation.

---

## Compiler — graph → skills.md

In `apps/web-creator/lib/builder/compile.ts` and mirrored server-side in `apps/api/src/creator/compile.py` (for re-compile on import + publish — single source of truth implementation; share via shape, not code).

Algorithm:

1. **Frontmatter** — assembled from the config form (see `03-skill-config.md`) + node aggregates:
   - `inputs[]` from all `parameter` nodes.
   - `outputs[]` from all `output` nodes.
   - `trigger_keywords` + `example_invocations` from the `context` node.
2. **Body** — fixed section order:
   - `## When to use` from context node's `description`.
   - `## Inputs` table from parameter nodes (one row each).
   - `## How to apply` from a topological walk of action + decision nodes:
     - Action → `1. {title}` then `instruction`.
     - Decision → `1. {title}` then `If {branches[0].label}: ...` etc.
   - `## Outputs` from output nodes.
   - `## Examples` from example nodes.
   - `## Limitations` — optional, from a special "limitations" note (if creator adds one — define `note.kind = "limitation"` as a typed note variant).
3. **Stable IDs** — emit hidden anchors before each step (`<!-- node:abc123 -->`) so the parser can map back.

Validate the result with `validateSkillsMd()` (the Zod-based browser equivalent of the backend validator). Render errors in the inspector / bottom bar.

## Parser — skills.md → graph

Best-effort. Used on import (Phase 4) and on re-opening a published skill into the builder.

1. Parse frontmatter → config form values.
2. Walk body:
   - `## When to use` → context node.
   - `## Inputs` rows → parameter nodes.
   - `## How to apply` numbered items → action nodes (or decision if "If ..." pattern).
   - `## Outputs` → output nodes.
   - `## Examples` → example nodes.
3. Use anchor comments (`<!-- node:... -->`) when present to preserve original IDs.
4. Lay out the graph: top-to-bottom flow, context on top, output at bottom, decisions diamond-style.

Note: parser is **not** a perfect inverse. We warn the user if structural info was lost ("This skill had custom sections we couldn't represent as nodes — they're in a 'note' for safe-keeping").

---

## Autosave

- On every mutation (drag, edit field, add/remove node/edge), update Zustand store immediately.
- Debounce 800ms then POST to `/v1/creator/skills/{id}/draft` with the full graph + frontmatter.
- Server upserts the `skill_drafts` row and re-runs the compiler + validator (fast, < 200ms for typical skills). Stores `compiled_md`, `compiled_valid`, `compile_errors`.
- Frontend reflects validation in real-time via the response.
- Status indicator: `Saved 2s ago` / `Saving…` / `Offline — will retry`.

Snapshots: a separate cron-ish trigger (every 10 min while session active, plus on publish, plus on import) writes `skill_draft_snapshots`. UI: "Restore version" menu in the top bar.

---

## API

- `GET /v1/creator/skills/{id}/draft` — returns the draft (graph + frontmatter + compile state).
- `PUT /v1/creator/skills/{id}/draft` — full upsert.
- `PATCH /v1/creator/skills/{id}/draft` — partial (used by autosave; idempotency via `If-Match` ETag).
- `POST /v1/creator/skills/{id}/draft/snapshots` — manual snapshot with label.
- `POST /v1/creator/skills/{id}/draft/restore/{snapshot_id}` — replaces current draft.
- `POST /v1/creator/skills/{id}/compile` — server-side compile + validate. Used by the publish wizard for the canonical result.

---

## UX polish

- Keyboard:
  - `Cmd/Ctrl+S` — manual save (rarely needed; autosave handles it).
  - `Delete` — remove selected nodes/edges.
  - `Cmd/Ctrl+Z / Shift+Z` — undo/redo within session (use `useUndoable` pattern in Zustand).
  - `Cmd/Ctrl+D` — duplicate selected.
  - Arrow keys nudge selected nodes by 8px.
- Minimap in bottom-right.
- Sticky help bubble: "?" → opens a short walkthrough overlay.
- Drag-to-create: drop a chip on canvas creates the node at cursor, auto-selects.

---

## Performance

- Skills with < 100 nodes should feel instant. Test with a 200-node synthetic graph; FPS ≥ 60 on mid-tier laptop.
- Inspector form changes don't re-render the whole canvas — use Zustand selectors.
- Compile is fast: < 100ms for typical skills. If it takes longer, surface a spinner in the validation pill.

---

## Acceptance

- [ ] All 7 node types are draggable from the palette and editable in the inspector.
- [ ] Compiler produces valid skills.md (validates green via `shared/skills-md-spec.md` validator).
- [ ] Parser round-trips a compiled file: compile → parse → compile produces byte-identical output (modulo anchor comments).
- [ ] Autosave debounces, retries on network failure, and reflects validation results.
- [ ] Snapshot + restore works.
- [ ] Undo/redo works for at least 50 operations.
- [ ] 200-node synthetic graph renders smoothly.
- [ ] Templates drop-in adds connected sub-graphs cleanly.
- [ ] E2E: create a new skill from blank → add 5 nodes → reach "valid" state → exit and re-open → state preserved.
