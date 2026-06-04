# Capture how-to

Every Skills Git creator can publish a **persona** — a collection of **memory neurons** drawn from real practitioner experience (situations, decisions, outcomes). Capture turns a freeform incident description into a structured neuron file linked into a parent occupation, so a buyer's agent can route their question into your lived experience the same way it routes into the curated methodology.

> **Reads:** [`team/04-capture-flow.md`](../team/04-capture-flow.md) for the underlying spec.
> See also [`docs/vault-format.md`](vault-format.md) for what your published neuron looks like inside a buyer's vault.

## Before you start

- You need a **creator account** on Skills Git.
- You need a **published parent occupation** to link your persona to. The Cycle-1 demo ships with [`skillsgit-curated/ai-devops-engineer`](../apps/api/scripts/seed_data/devops/occupation.yaml); the future `/occupations` browse page will list every published occupation.
- Your persona needs to exist before you can capture into it. Create one via `POST /v1/personas` with `parent_occupation_id` pointing at the published occupation slug.
- The platform extracts your draft using a **metered Claude key** (default `claude-sonnet-4-6`). Free tier: **10 captures/month** per creator. BYOK (bring-your-own-key) is on the Cycle 2 roadmap.

## The 4-field form

`/capture/[id]` collects exactly four free-text fields plus optional attachments. Aim for plain prose — the LLM extracts structure from your wording, so write it the way you'd tell a coworker.

1. **Title** — one line. The slug is auto-suggested from this.
2. **Situation** — what was happening, when, who was involved (3–10 sentences).
3. **Decision** — what you decided and why (2–5 sentences).
4. **Outcome** — what happened next, would you do it again (2–5 sentences).
5. **Context** (optional) — tools, dates, team size, anything that helps the AI understand scope.
6. **Attachments** (optional) — screenshots, config snippets, RCAs. Each ≤5 MB; content-addressed in storage.

Click **Generate draft**. The form submits to `POST /v1/capture/sessions` and enqueues an extraction job. See [`team/04-capture-flow.md`](../team/04-capture-flow.md) §1 for the full wireframe.

## What the AI does

A background Arq worker calls Claude with a structured prompt (system prompt + your four fields + the parent occupation's candidate link targets). Within ~30 seconds it writes back a **draft memory-neuron `.skills.md` file** with:

- **Frontmatter** — `kind: memory_neuron`, `parent_occupation_id: <handle>/<slug>`, the structured `neuron` block (`situation`, `decision`, `outcome`, `recorded_at`, `confidence`), and `links:` suggestions drawn from the occupation's member skills.
- **Body** with the canonical sections — `## When to use`, `## How to apply`, and (optionally) `## What happened`, `## Lessons`.

You land on the draft-review view. You can:

- **Edit anything** — change the markdown, rewrite the situation block, adjust suggested tags.
- **Re-run extraction** — costs another capture against your monthly quota. Manual edits are lost on re-run; the UI confirms before clobbering.
- **Resolve PII flags** (see below).
- **Confirm or reject suggested links** (see below).
- **Publish** — submits to `POST /v1/capture/sessions/{id}/finalize`.

On publish, the platform re-runs `validate_file()`, hard-blocks on any high-severity PII, then inside a single DB transaction:

1. Creates a `skills` row (`kind=memory_neuron`, `status=draft`, your handle as creator).
2. Creates a `skill_versions` row at `1.0.0`.
3. Adds the neuron to your persona via `persona_neurons` with the next sort_order.
4. Promotes draft attachments from `attachments/captures/{session_id}/` to `attachments/personas/{persona_id}/` via S3 server-side copy.

Any failure rolls back everything. Your draft is private until you click Publish — it never appears in any catalog query, and the 456-skill curated library is unaffected.

## PII handling

The platform performs **detection** at extract time; you perform **resolution** before finalize. Two tiers:

- **Hard blocks** (always reject finalize): real credit-card numbers, real SSNs, AWS access keys, private keys, generic API-key shapes. These are detected by the existing `SECRET_PATTERNS` in the validator and never make it into the vault.
- **Warn list** (you decide): emails, phone numbers, IPv4 addresses, internal Slack channel mentions, Jira ticket IDs. Each flag is shown with the span and a `suggested_redaction`. You can **keep**, **redact** (replace with `[REDACTED]`), or **edit** the surrounding prose manually.

The platform never auto-redacts — a memory neuron loses meaning if names and timestamps are stripped without your judgment. See [`team/04-capture-flow.md`](../team/04-capture-flow.md) §4 for the full detector table and severity rules.

## Linking into an occupation

Each neuron should `links[]` to 2–4 base-occupation skills it relates to. The AI proposes; you confirm. `relation` values:

- **`applies`** — this neuron is an instance of that methodology in action.
- **`extends`** — this neuron adds to that methodology (a new case, a refinement).
- **`see-also`** — related context, useful but not directly applied.
- **`contradicts`** — this neuron records a case where the methodology didn't work.
- **`recorded-instance-of`** — narrower than `applies`; this neuron is a specific recorded run.

Link targets are bare slugs against the parent occupation's members: `base/ci-pipeline-architect`, not the full vault path. The composer resolves them at delivery time when your persona is layered into a buyer's vault — broken links are surfaced in `manifest.warnings[]` rather than blocking the build.

The AI MUST pick targets from the parent occupation's actual skills (the prompt constrains it to a candidate list), so suggestions always resolve at the parent's current state. If the occupation later renames a skill, your next persona rebuild surfaces a warning so you can re-link.

## Publish + payout

- **Free for MVP.** Personas land for free during Cycle 1; paid personas with revenue split are on the Cycle 2 roadmap.
- Once published, your persona appears in the marketplace under your creator handle. Buyers who already hold an **active license to the parent occupation** can subscribe to your overlay. The checkout API returns `409 persona.requires_parent_occupation` (with the parent's slug) if a buyer tries to purchase without it.
- **Updates.** Edit a neuron → the patch version bumps automatically (1.0.0 → 1.0.1). The persona's next vault build picks it up. Existing subscribers see a "new build available" badge and re-download to receive the change.

## Worked example

This is one of the seeded `@jane-devops-demo/incident-veteran` neurons (sample data; the file lives at [`apps/api/scripts/seed_data/devops-persona/neurons/2024-08-flaky-tests-after-redis-upgrade.skills.md`](../apps/api/scripts/seed_data/devops-persona/neurons/2024-08-flaky-tests-after-redis-upgrade.skills.md)).

### Form input

| Field | What was typed |
|---|---|
| **Title** | `Flaky integration tests after Redis 7.2 upgrade — Aug 2024` |
| **Situation** | Eighteen hours after a Redis Cluster 7.0 → 7.2 minor upgrade on the shared CI Redis pool, the checkout-service integration suite started timing out 35% of nightly runs. No application code had changed for 36 hours, and the unit-test tier was green. |
| **Decision** | Pinned Redis 7.0 across CI via the cluster-image tag, opened an incident, then bisected the integration-test harness against 7.2 in a one-off branch. Confirmed that the WAIT command semantics changed so a single assertion that expected acknowledgement in 10s now took up to 35s under load. |
| **Outcome** | Reverted to 7.0 immediately (CI back to green in 12 minutes). Over the next two weeks rewrote the `assert_eventually()` helper to drive its timeout from a per-test budget rather than a hardcoded 10s constant, then re-rolled 7.2. Zero flakiness on the new helper across the next 600 nightly runs. |
| **Context** | Team of 8, ~200 backend tests, GitHub Actions matrix, Python 3.12. |

### AI-extracted draft (key fields)

```yaml
---
id: jane-devops-demo/2024-08-flaky-tests-after-redis-upgrade
version: 1.0.0
name: 2024-08 Flaky integration tests after Redis 7.2 upgrade
description: "CI suite timed out 35% of nightly runs starting 18 hours after a Redis Cluster 7.0->7.2 minor upgrade; bisected to a WAIT semantics change."
kind: memory_neuron
parent_occupation_id: skillsgit-curated/ai-devops-engineer
tags: [ci, redis, flaky-tests, bisect]
links:
  - target: base/ci-pipeline-architect
    relation: applies
  - target: base/gha-workflow-optimizer
    relation: see-also
  - target: base/chaos-experiment-planner
    relation: see-also
neuron:
  situation: |
    Eighteen hours after a Redis Cluster 7.0 -> 7.2 minor upgrade...
  decision: |
    Pinned Redis 7.0 across CI via the cluster-image tag...
  outcome: |
    Reverted to 7.0 immediately (CI back to green in 12 minutes)...
  recorded_at: "2024-08-22"
  confidence: 0.9
---
```

### Suggested links the AI proposed

- `base/ci-pipeline-architect` — applies (confidence 0.9, pre-checked)
- `base/gha-workflow-optimizer` — see-also (confidence 0.8, pre-checked)
- `base/chaos-experiment-planner` — see-also (confidence 0.7, pre-checked)

The creator confirmed all three.

### What landed in the vault

After publish, the persona's next build wrote the file to:

```
personas/jane-devops-demo/incident-veteran/neurons/
    2024-08-flaky-tests-after-redis-upgrade.md
```

With:

- The full frontmatter (above) plus the auto-generated `distribution:` signing block.
- A body with `## When to use`, `## How to apply`, `## What happened`, `## Lessons` sections.
- An auto-generated `## Linked notes` footer with three `[[wiki-links]]` to the base occupation's resolved paths.
- The trailing `<!-- skg-attribution: ... -->` comment (vault_path, skill_id, version, kind, creator_handle, content_hash, built_at).

A buyer's agent loading the composed `vault.json` sees this neuron as one entry in `files[]` with `kind: memory_neuron` and the full `neuron` block mirrored for fast routing. See [`docs/vault-format.md`](vault-format.md) for the consumer-side view.
