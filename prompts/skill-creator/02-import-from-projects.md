# skill-creator — 02 Import from Existing AI Projects

**Phase:** 4
**Depends on:** `skill-creator/00-overview.md`, `skill-creator/01-visual-builder.md`, `shared/skills-md-spec.md`
**Parallel-safe with:** `03-skill-config.md`, `04-test-and-preview.md`, `05-publish-to-marketplace.md`
**Status:** ready
**Owner:** _empty_

> Most creators already have prototypes living elsewhere. Import is the fastest path from "I have an idea" to "I have a draft". This prompt covers four source platforms; the architecture is extensible to more.

---

## Scope

Importers for:

1. **Claude Code SKILL.md / skills.md files** (drop-in, fastest path).
2. **OpenAI Custom GPTs** (URL share link, or JSON export from the OpenAI editor).
3. **OpenAI Assistants** (Assistant ID + API key, OR exported JSON).
4. **OpenAI Codex projects** (zip upload; the legacy Codex playground format is `.txt` instruction sets — treat as raw markdown).

For each, the result is the same: a populated `skill_drafts` row that opens in the builder.

---

## Import wizard (`/import`)

Step 1 — choose source. Cards:
- "I have a skills.md file" → file upload.
- "OpenAI Custom GPT" → URL or JSON.
- "OpenAI Assistant" → API key + assistant ID OR JSON.
- "Codex project" → file upload (.zip or .txt).
- "Paste prompt or instructions" → freeform textarea (fallback path: AI-extracts structure).

Step 2 — provide input.

Step 3 — preview the extracted draft. Show frontmatter and a tree of nodes that would be created. Allow inline edits before commit.

Step 4 — pick a slug + name (pre-filled from extraction). Create the skill in `draft` state with the graph populated. Redirect to `/skills/{id}/builder`.

---

## Importer architecture

```
apps/api/src/importers/
├── base.py             ImportResult dataclass; abstract base
├── skills_md.py        the lossless one
├── openai_gpt.py
├── openai_assistant.py
├── codex.py
├── freeform.py         the LLM-driven fallback
└── normalize.py        common post-extraction normalization
```

Each importer exposes `def import_from(...) -> ImportResult`. `ImportResult` is:

```python
@dataclass
class ImportResult:
    frontmatter: dict           # partial; missing keys filled by user later
    nodes: list[NodeStub]       # NodeStub: kind, data
    edges: list[EdgeStub]
    warnings: list[str]         # surface to the user
    raw_source_blob: str        # for audit + re-import
    confidence: float           # 0.0–1.0; affects UI cue
```

API endpoint:
```
POST /v1/creator/imports
  body: { source: "claude_skill"|"openai_gpt"|"openai_assistant"|"codex"|"freeform",
          payload: <varies by source> }
  → ImportResult JSON
```

Always idempotent: same payload returns the same result (modulo timestamps).

A second endpoint commits the result into a draft:
```
POST /v1/creator/skills
  body: { from_import: <import_id>, slug, name }
  → Skill (draft)
```

Imports are persisted to `imports` table for audit:

| col | type |
|---|---|
| id | uuid pk |
| user_id | uuid fk |
| source | text |
| raw_blob | jsonb |
| result_json | jsonb |
| warnings | text[] |
| committed_skill_id | uuid fk → skills.id (nullable until used) |
| created_at | timestamptz |

---

## 1. Claude Code SKILL.md import

Easiest case — the file IS already a skills.md (or close to it).

- Run our parser (`apps/api/src/skills/parser.py`).
- If frontmatter is missing fields, fill defaults + flag as `warning`.
- Map body sections to nodes per `01-visual-builder.md`'s parser rules.
- Confidence: 0.95 typical.

Accepts:
- Direct file upload.
- A URL to a Claude Code skill repo (parse `SKILL.md` or `skills.md` from repo root; if it's a public GitHub URL, fetch via the GitHub API). Phase 4 supports GitHub URLs only; other hosts deferred.

---

## 2. OpenAI Custom GPT import

A Custom GPT has:
- A name + description.
- Instructions (the system prompt) — a multi-paragraph chunk of text.
- Conversation starters (1–4 short prompts).
- Knowledge files (PDFs, etc.) — we DON'T import the files; we flag them as "external knowledge expected" and add a warning.
- Capabilities flags (web browsing, code interpreter, DALL·E, actions). Map to `tools_required`.

**Two input methods:**

a) **JSON export** — the user pastes the JSON the OpenAI editor produces. Parse fields directly.

b) **Share URL** — `https://chatgpt.com/g/...` — Phase 4 best-effort. The OpenAI URL is render-only and has no public API; for v1 we attempt to fetch the HTML and parse the metadata. If that fails, prompt the user for JSON. (Document this limitation in the UI.)

**Extraction:**
- `name` → `frontmatter.name`
- `description` → `frontmatter.description` (truncate to 280)
- `instructions` → run through `freeform.py` to split into context + steps → seed builder nodes.
- `conversation_starters` → `example_invocations[]`.
- Capability flags → `tools_required[]`.
- Knowledge files → warning + a "note" node listing filenames.

Confidence: 0.75 typical (instructions structure varies wildly).

---

## 3. OpenAI Assistant import

The Assistant API exposes more structure: instructions, tools (file_search, code_interpreter, function calling), model, file IDs.

**Input methods:**

a) **API key + Assistant ID** — server-side, the importer calls `openai.beta.assistants.retrieve(...)`. The user's OpenAI API key is requested, used once, never stored (zero-out memory after use). Show explicit "We need your key for one call" UI with a "Why?" link explaining.

b) **JSON export** — same shape as the Assistant API response. Paste-able.

**Extraction:**
- `name`, `description`, `instructions` → same as GPT.
- `model` → frontmatter.ai.required_models (mapped from OpenAI model ids).
- `tools[]` → `tools_required[]`. file_search → `["file_search"]`; code_interpreter → `["code_execution"]`; functions → flag as "actions" but don't auto-import the schemas (warn).
- `file_ids[]` → warning about external knowledge.
- Temperature, top_p, response_format → metadata-only fields stored in raw_blob; the builder doesn't represent these as nodes.

Confidence: 0.85.

---

## 4. Codex project import

Codex is mostly legacy (OpenAI's old completion API era). Inputs we see in practice:
- `.txt` files of instruction sets (essentially big system prompts).
- `.zip` containing multiple `.txt` files + maybe a README.

**Extraction:**
- Concatenate all `.txt` files; if a README exists, use it for description.
- Run through `freeform.py` to extract structure.

Confidence: 0.60. Most Codex imports will need significant manual cleanup.

---

## 5. Freeform fallback

For "Paste prompt or instructions" and as a sub-step inside GPT/Codex importers:

A server-side LLM call (Claude) extracts structure from raw text. The prompt instructs:
- Identify the "when to use" statement → context node.
- Identify numbered or implicit steps → action nodes.
- Identify any branching ("if X then Y") → decision nodes.
- Identify input slots and expected outputs.
- Suggest 5 trigger keywords and 2 example invocations.
- Return JSON in our `ImportResult` schema.

**Cost & latency:** budget ≤ 8k input tokens + ≤ 4k output. p95 < 8s. Cache by hash of input to avoid re-running.

**Privacy:** the raw text is sent to Claude (our platform key). Disclose this in the import UI: "We'll use Claude to extract structure from your text. Your text is not stored beyond this import."

Confidence: 0.50–0.80 depending on input quality.

---

## Post-extraction normalization (`normalize.py`)

After any importer returns, run:

1. **Layout** — assign positions to nodes (top-down, context on top, output on bottom).
2. **Slug suggestion** — derive `id` slug from name (kebab-case, dedupe against creator's existing skills).
3. **Validation pass** — run the validator; capture errors as `warnings`, do not block.
4. **Confidence cues** — flag low-confidence nodes (e.g., a decision with only one branch) with a "Review me" badge in the inspector when the draft opens.

---

## UI for the preview step

- Left: frontmatter form pre-filled.
- Right: node tree preview (collapsed by section). Click a node to expand and see its data.
- Bottom: warning list.
- "Looks good — open in builder" button.

After commit, the builder opens with a tour: "We populated 12 nodes from your import. Pink dots are low-confidence — review before publishing."

---

## Acceptance

- [ ] All 4 source importers work against fixture files in `apps/api/tests/fixtures/imports/`.
- [ ] Freeform fallback returns valid `ImportResult` for at least 5 hand-curated test inputs (varying quality).
- [ ] Confidence score is plumbed end-to-end and shown in the UI.
- [ ] Each importer's `warnings[]` surfaces clearly in the preview step.
- [ ] An imported draft opens cleanly in the builder with a guided tour highlighting flagged nodes.
- [ ] OpenAI API key (Assistant flow) is never persisted; verified by a test that checks Redis/DB doesn't contain the key after import.
- [ ] E2E: paste a GPT JSON → see preview → commit → builder opens with a sane graph.
