# 06 — Open Questions

**Owner:** Architect
**Status:** **GATING — must be answered by the user before Cycle 1 begins.**
**Read:** every prior `team/` file. Each question links back to the
files it touches.

These are decisions I cannot make alone — they encode product / pricing /
trust intent that should come from you. Each has a recommendation; if you
agree with all six recommendations, write "approve all" and Cycle 1
starts immediately.

---

## Q-1 — Persona pricing tiers + creator-payout split when bundled

**Why it matters:** ADR-002 keeps the persona purchase separate from the
occupation purchase, which means Stripe Connect transfers cleanly to two
different creators on two separate transactions. But buyers will ask for
a bundled "occupation + persona" checkout, and creators will ask for
a "discount when bought together" lever. Both touch pricing and
payouts.

**Options:**
- **A. Persona price is free for MVP.** Every persona ships at
  `pricing_model=free`. The platform takes no fee. We avoid the
  bundling and split questions entirely. This is consistent with the
  current `publish_curated.py` policy of free skills.
- **B. Persona is paid (one_time only) with platform fee per existing
  rules.** No bundling. Buyer buys the occupation first, then the
  persona at full sticker. Two transactions, two Stripe Connect
  transfers, two `transfer_data.destination` accounts. Simple, well-
  understood, but no discount.
- **C. Persona is paid AND we offer a "bundled checkout" that combines
  the occupation + 1+ personas into a single Stripe Checkout with
  multiple `line_items` and per-line-item `application_fee_amount` and
  `transfer_data.destination`.** Stripe supports this via separate
  charges in a single Checkout but not multi-creator-destination
  splits within one Checkout; we'd actually have to fan out into N
  sequential payment intents under the hood. Doable but adds real
  complexity, plus the discount logic needs a new table.

**Recommendation:** **A** for the MVP (free personas), then **B** as
the first monetization step after the demo lands. Keeps the demo
mechanically identical to the existing 456-skill flow. **C** waits for
real demand and a Phase-2 ADR.

---

## Q-2 — Capture AI extraction: platform key (metered) vs. BYOK

**Why it matters:** ADR-008 locked platform-key Claude for MVP, but
the underlying concern is cost predictability + privacy. A creator
recording a sensitive incident might prefer to send the data to *their
own* Anthropic key, not ours. We also pay the bill in the platform-key
model.

**Options:**
- **A. Platform key only, free 10/month, no BYOK escape valve in MVP.**
  Matches ADR-008 as written. Cheap, easy. Creators sensitive about
  data trust the platform's privacy promise (or don't use capture).
- **B. Platform key as default, BYOK as an opt-in via a new
  `creator_api_keys` table.** Add a "Use my own Anthropic key" toggle
  in `/settings`. The key is stored encrypted (libsodium or `cryptography`'s
  Fernet). Adds a table, a settings panel, and an env-var management
  surface. ≈ 1-2 days of work on top of the MVP.
- **C. BYOK only — no platform key.** Forces every creator to bring a
  key. Highest privacy posture. Worst onboarding friction (a creator
  needs an Anthropic account before they can capture). Demo-killer.

**Recommendation:** **A** for MVP (ADR-008 stands). Add a BYOK toggle in
Cycle 2 when the demo's stable. The capture pipeline architecture
doesn't care which key is used — the LLM client is centralized — so
this is a clean future change.

---

## Q-3 — "DevOps engineer who never publishes" trial flow

**Why it matters:** A practitioner might want to use the capture UX
purely as a personal knowledge tool — record situations, run their
agent against their captured memory — without ever publishing a
persona to the marketplace. Today the spec couples capture to a
persona row (and personas to publication).

**Options:**
- **A. No private mode. To capture, you must own a persona row, and
  that persona row is a marketplace listing (draft, unlisted, or
  published).** Simplest. Creator pollutes their dashboard with a
  "Personal" persona they keep in draft forever.
- **B. Add a `personas.is_private` flag. Private personas never list
  on the marketplace, but are valid composition targets for the
  owner's own composed vault downloads.** This means a creator can
  download `occupation + their_private_persona`. We allow this
  because the persona's neurons are theirs and they paid for the
  occupation. No revenue impact.
- **C. Full "personal vault" mode — uncouple captures from personas.
  Creator captures into a generic personal bucket and gets a vault
  built from that bucket + any occupation they own.** Most flexible,
  most engineering. Adds a `personal_vault` table and a separate
  composer path.

**Recommendation:** **A** for MVP (zero schema changes), **B** for
Cycle 2 if even one user asks (one column add). **C** waits for
explicit demand and a real use case beyond "I'd rather not publish".

---

## Q-4 — Sample personas for the demo: ship our own seeded persona, or recruit a real creator?

**Why it matters:** The demo (Layer C) needs at least one persona
overlay. T-12 in the MVP plan seeds a `@jane-devops-demo` persona with
5–10 hand-authored neurons. This is fine for the demo but creates a
"seeded by us" credibility footprint. The killer feature ("real
practitioner memory") is more believable if a real DevOps engineer
publishes the first persona.

**Options:**
- **A. Ship our own seeded persona as `@jane-devops-demo`, clearly
  labeled as a demo/example.** Fast, controllable, ready when the
  demo runs. Risk: looks fake.
- **B. Recruit one real DevOps engineer to publish a persona before
  the demo.** Real credibility but a 1-2 week timing risk —
  recruiting + onboarding + their time writing 5+ real neurons.
- **C. Both.** Ship the seeded `@jane-devops-demo` as a placeholder;
  recruit a real practitioner in parallel; swap in their persona for
  the demo if they're ready in time, else fall back.

**Recommendation:** **C**. Seeded persona unblocks T-13 and QA; a real
practitioner persona is a marketing upgrade if it lands. Demand the
seeded persona's `description_md` explicitly says "sample data" so
nobody mistakes it.

---

## Q-5 — NSFW / IP policy for captured situations

**Why it matters:** A creator can paste anything into the capture
form: confidential customer info, regulated medical data, code from a
former employer they shouldn't share. ADR-008 hands off responsibility
to the creator (they own it), but we need a defensible position when
something inevitably leaks.

**Options:**
- **A. Terms-of-service-only.** Creators agree they own/have rights to
  what they capture; the platform disclaims. PII scanner flags but
  doesn't block. Matches our current marketplace stance on user-
  generated content.
- **B. Hard-block on a small forbidden-content list at finalize
  (HIPAA-flag keywords, CCN, SSN — many already in
  `SECRET_PATTERNS`). Soft-warn on a broader list (customer
  names — TBD source).** Most defensible but the warn-list is hard to
  curate without per-creator customization.
- **C. Same as B, plus require explicit per-neuron labeling: every
  finalized neuron has a `confidentiality` field (`public`, `industry`,
  `internal`). Only `public` are eligible to be sold. `internal` can
  only compose into the owner's private vault (depends on Q-3).**
  Most rigorous, also the most product surface to build.

**Recommendation:** **A + the existing SECRET_PATTERNS hard-block + the
MVP `pii_patterns` warn list from `04-capture-flow.md`**. We already
block real credentials, and we flag obvious PII for the creator to
decide. Going further requires a legal / trust-and-safety motion that
shouldn't be on the critical path for the demo. Document this stance
on the capture page.

---

## Q-6 — Vault format extensions: ship a `.obsidian/` config dir with sane graph defaults?

**Why it matters:** The vault opens in stock Obsidian without any
configuration (ADR-011). But the graph view's defaults (white nodes,
gray edges, no color-by-tag) are visually bland — the demo will land
better if the graph "looks designed". An `.obsidian/graph.json` of
≈100 bytes can color-by-tag with our brand palette and set the
default search behavior.

**Options:**
- **A. No `.obsidian/` directory.** Stock Obsidian opens the vault
  with its own defaults. Reproducible, minimal.
- **B. Include `.obsidian/graph.json` with a small color-by-tag preset
  matching brand palette, plus a `.obsidian/workspace.json` that opens
  `00-index.md` on first open.** Tiny override. Demo-friendly. Risk:
  Obsidian future versions might warn about loading an unknown
  workspace file, though it's been stable for years.
- **C. Ship a small Obsidian *plugin* (a sidebar that surfaces
  `vault.json` attribution as a hover card).** Most polished, also
  the most engineering. Adds a non-trivial dependency on Obsidian
  plugin APIs.

**Recommendation:** **B** for the demo. ≈ 30 minutes of work in T-08
(curation). Document the override in `docs/vault-format.md`. Stay away
from C — that's a Phase-2 product surface.

---

## TL;DR — answer template

If you accept every recommendation, reply:

> approve all

If you want to override specific items, reply with just the deltas:

> Q-1 → B, Q-3 → B; approve rest

Once approved, Cycle 1 implementation agents are spawned per
`team/05-mvp-plan.md`.

---
