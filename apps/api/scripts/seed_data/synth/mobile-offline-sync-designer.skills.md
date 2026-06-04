---
id: skillsgit-curated/mobile-offline-sync-designer
version: 1.0.0
name: Mobile Offline Sync Designer
description: Design conflict-free offline sync for a mobile app — choose between last-write-wins, operational transform, CRDTs, or manual merge UIs based on data shape and collaboration mode.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:mobile-dev, offline-first, sync, crdt, conflict-resolution, local-first, ios, android]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 48000
  estimated_tokens_per_invocation: 10000
trigger_keywords:
  - offline sync design
  - offline first
  - conflict resolution
  - lww sync
  - crdt design
  - operational transform
  - mobile sync engine
  - local first app
  - offline editing
  - merge ui design
  - eventual consistency mobile
example_invocations:
  - "We need offline editing for a notes app with shared notes. Walk us through a sync design."
  - "Our team-collab to-do app gets duplicate items after offline edits. Diagnose and propose a fix."
  - "Design an offline sync layer for our field-service app that captures forms in tunnels and uploads later."
inputs:
  - name: app_description
    type: text
    required: true
    description: What the app does, what data the user edits offline, and who else can edit the same data.
  - name: collaboration_mode
    type: choice
    required: true
    description: Who edits the same data.
    choices: [single-user-multi-device, small-team-collaborative, mass-collaborative, single-user-single-device-with-restore]
  - name: data_shape
    type: choice
    required: true
    description: Dominant shape of the data being synced.
    choices: [discrete-records, ordered-list, free-text-document, structured-tree, key-value-counters, mixed]
  - name: connectivity_profile
    type: choice
    required: false
    description: How often the device is offline. Defaults to "intermittent".
    choices: [usually-online, intermittent, often-offline, sometimes-offline-for-days]
  - name: must_have_constraints
    type: text
    required: false
    description: Anything binding the design — regulated data retention, no third-party libs, encryption at rest, audit trail.
  - name: existing_stack
    type: text
    required: false
    description: Current persistence (SQLite, Realm, Core Data, Room, Hive, MMKV), framework, and backend (REST, GraphQL, custom).
outputs:
  - name: design_document
    type: markdown
    description: Structured design — data model, sync protocol, conflict policy, UI affordances for unresolvable conflicts, and failure-mode catalogue.
  - name: data_model_sketch
    type: markdown
    description: Schema fragments for the local store and the sync payload, with version, vector clock or hybrid-logical-clock fields as needed.
  - name: test_plan
    type: markdown
    description: Scenarios the design must pass — concurrent edits, deletes during edits, clock skew, partial sync, app uninstall and reinstall.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Mobile Offline Sync Designer

## When to use

Reach for this skill when a mobile app needs to work when the network is gone — a notes app on a flight, a field-service app in a basement, a chat app on a subway — and the team has not yet decided how conflicts will be handled. Offline sync looks like a feature; it is actually a distributed-systems problem squeezed into a phone. Getting it wrong is hard to fix later because the failure mode is "user lost data" and the fix is often a schema migration on already-deployed clients.

Use the skill when:

- A new app's product spec includes "works offline" and the engineering team has not yet picked a conflict-resolution strategy.
- An existing app shows duplicate records, missing items, or "version mismatch" errors after offline edits.
- A team is migrating from a simple `last-modified-wins` model and now needs to support team collaboration where last-write-wins is no longer acceptable.
- A team is evaluating a managed sync service (Realm Sync, Firestore offline, PowerSync, Supabase Realtime) and wants to know what they would build if they wrote it themselves, to evaluate the trade.

Do not use it for:

- Caching server responses for performance. That is a much simpler problem (HTTP cache + staleness policy) and is not what this skill solves.
- Pure client-side persistence with no backend. There are no conflicts to resolve.
- Designing the backend infrastructure for sync; the skill focuses on the client design and the wire contract.

## Inputs

- `app_description` (required) — Without product context the design is generic. Include the data that gets edited offline.
- `collaboration_mode` (required) — This is the single most important input. The right sync design for one user with two devices is completely different from the design for a hundred users editing one document.
- `data_shape` (required) — Discrete records have different conflict patterns than ordered lists or free text.
- `connectivity_profile` — Drives sync cadence, retry, and storage budget.
- `must_have_constraints` — Regulated audit trails, GDPR deletion, no-third-party policies. Each removes design options.
- `existing_stack` — Determines what is feasible without a rewrite.

## How to apply

Design proceeds in seven phases. Stop after each one and check that the user agrees before continuing — these decisions are sticky once code ships.

### 1. Frame the problem

Write the first paragraph of the design document. It contains:

- The actor (one user multi-device, small team, many users).
- The unit of data (a note, a task, a row, a document, a counter).
- The unit of edit (whole-record replace, field patch, ordered list mutation, text edit).
- The expected sync cadence (continuous, on app foreground, on Wi-Fi, on user action).
- What "correctness" means to the product. "No data loss" and "convergent state" and "intent preservation" are different goals and often conflict.

Then write the single most important constraint: what would the user consider an unacceptable failure? "Two users see different lists" is unacceptable in a checkbox app; "two paragraphs got reordered" is unacceptable in a document editor.

### 2. Pick a conflict policy from the menu

The candidate policies, with the cases each one fits:

**Last-Write-Wins (LWW)**

- One winner per field or per record, determined by timestamp.
- Fits: single-user-multi-device on discrete records (settings, profile attributes, single-author notes).
- Does not fit: collaborative editing, where it silently destroys work.
- Pitfall: timestamps from device clocks are not trustworthy. Use a hybrid logical clock or a server-issued sequence to disambiguate.

**Last-Write-Wins with field-level merge**

- LWW per field rather than per record. Two devices editing different fields of the same record both keep their edits.
- Fits: single-user-multi-device with partial edits (a contact card where one device edited the email and another edited the phone).
- Does not fit: ordered lists or trees.

**Operational Transform (OT)**

- Each edit is an operation; concurrent operations are transformed against each other before being applied.
- Fits: collaborative free-text editing where intent preservation matters.
- Does not fit: small teams who do not want to run a centralised OT server; OT typically needs a server-of-record.
- Pitfall: implementing OT correctly is a multi-engineer-quarter project. Use a battle-tested library or pick another policy.

**Conflict-free Replicated Data Types (CRDTs)**

- Data types designed so concurrent replicas converge mathematically regardless of order. Common variants for mobile:
  - **G-Counter / PN-Counter** for monotonically growing or signed counters (likes, votes).
  - **OR-Set / 2P-Set / Add-Wins-Set** for sets where add/remove conflict.
  - **LWW-Element-Set or Add-Wins-Map** for record collections keyed by id.
  - **RGA / Yjs / Automerge text** for collaborative text and rich text.
  - **Replicated trees** (e.g. Tree-CRDT) for hierarchical structures like file systems and outlines.
- Fits: collaborative editing without a central server-of-record, or with eventual server sync where you accept that the client and server can diverge for a while.
- Does not fit: situations with strong server-side authority (banking, ticketing) where you need the server to reject conflicting edits.
- Pitfall: storage cost can grow with edit history; pick a CRDT with garbage collection (compaction) or schedule pruning.

**Manual merge UI**

- When the system cannot resolve, ask the user. Show "yours" and "theirs" and let the user pick or merge.
- Fits: structured documents where the user cares about intent and would rather decide than have the system guess (project plans, configuration).
- Does not fit: high-frequency edits or unattended sync.
- Pitfall: a manual merge UI that fires every few minutes is rage-inducing. Use only as a fallback after automated rules.

**Append-only event log with server reconciliation**

- Clients append events locally and to the server; the server resolves; clients reconcile to the server's snapshot.
- Fits: workflows where the server has authority (orders, payments, audit trails) but the client must continue offline.
- Pitfall: requires a stable event schema and migration plan for old clients.

### 3. Apply the data-shape filter

Cross-reference the policy menu with `data_shape`:

| Data shape | Default policy | Alternative |
|---|---|---|
| Discrete records, single editor per record | LWW per record | Field-level LWW for partial edits |
| Ordered list (to-do items, queue) | OR-Set + ordering CRDT (RGA, Logoot) | Manual merge for short lists |
| Free-text document | CRDT (Yjs, Automerge text) or OT | Manual merge for low-frequency edits |
| Structured tree (outline, file system) | Tree-CRDT | Append-only events + reconcile |
| Counters | G-Counter / PN-Counter | Append-only deltas reconciled server-side |
| Key-value scratch data | LWW | Field-level LWW |
| Mixed | Per-feature decision | n/a |

Write the choice and the runner-up. Be honest about which conflicts the chosen policy will mis-handle, and how the product will surface those.

### 4. Design the local data model

Local persistence has to track three things beyond the user-visible data:

4.1. **Identity**. Every record needs a globally unique id assigned at creation, not by the server. UUID v4 or v7 is fine; integer auto-increment is not, because it requires a server round-trip to mint. Without client-side ids, offline-created records duplicate after sync.

4.2. **Causality**. Track which client and which logical time produced each edit. The cheapest viable choice is a hybrid logical clock (HLC) per device, stored alongside each record. HLCs combine a wall-clock timestamp with a logical counter so concurrent edits from the same device order correctly even if the clock jumps. For full CRDTs, use a vector clock or the library's built-in clock.

4.3. **Sync state**. Each record carries: `local_version`, `last_synced_version`, `pending_ops` (or a dirty flag), `tombstone` (for deletes), and optionally `conflict_with` (an id of a competing version awaiting manual merge).

The local schema therefore looks roughly like:

```
records(
  id TEXT PRIMARY KEY,
  payload BLOB,
  hlc_timestamp TEXT,
  device_id TEXT,
  local_version INTEGER,
  last_synced_version INTEGER NULL,
  is_tombstone INTEGER,
  conflict_with TEXT NULL
)
```

CRDT-backed apps add an ops log table or store the CRDT structure directly (Automerge's binary format, Yjs's `Y.Doc` encoded as bytes).

### 5. Design the sync protocol

The protocol covers four operations:

5.1. **Push**. Client sends `since_version` and a batch of `pending_ops` or full records. Server responds with accepted ids and a new server-issued version.

5.2. **Pull**. Client sends `since_version`; server streams changes back. For CRDTs, this is "send all ops since X." For LWW, it is "send all records updated since X."

5.3. **Acknowledge**. Client persists the new version and clears the pending flag. This is non-trivial: the operation must be atomic so that a crash between server-success and local-ack does not double-send or lose track. Wrap in a local transaction; never trust an in-memory flag.

5.4. **Conflict surface**. If the server detected an unresolvable conflict (rare for CRDTs, common for LWW with field-level merges), it returns both sides and the client stores them with `conflict_with` set, prompting the merge UI.

Wire format choices:

- JSON over HTTPS is fine for small payloads; ProtoBuf or FlatBuffers for high-volume sync.
- Use **etag-style version tokens**, never raw timestamps for sync cursors. Timestamps go backward with clock skew; tokens don't.
- Include **device_id** in every request; the server uses it for diffing and rate-limiting per device.

Cadence and triggers:

- On app foreground.
- After every meaningful user mutation, if online (debounced 250-500 ms).
- On a background fetch (iOS BGAppRefreshTask, Android WorkManager periodic) — at most every 15 min on iOS, every 15-30 min on Android, subject to the OS.
- On network state change from offline to online.
- On user pull-to-refresh, with a "force full re-sync" path for rare situations.

### 6. Design the UI surface for the failure modes

Each failure mode the policy cannot resolve needs a UI:

- **Stale data shown to the user**: a "syncing..." indicator and a timestamp ("Last synced 3 minutes ago"). Avoid a permanently-visible cloud icon; users learn to ignore it. Surface only when stale beyond a threshold.
- **Conflicts requiring manual merge**: a non-modal banner the user can dismiss to keep working; a dedicated conflict-resolution screen.
- **Permanently-failed records**: a "sync error" affordance on the record; never silently drop.
- **Records edited offline, then deleted upstream**: show the local copy with a "restore or discard" prompt.
- **Records the user thinks they edited but never synced**: show the unsynced state explicitly. Many users do not check connectivity before editing.

A common subtle bug: an edit field that is reactive to server changes will overwrite a user's in-progress typing when a sync lands. Either freeze fields while the user is editing them or merge the incoming change with the live cursor position.

### 7. Plan the test matrix

Offline sync bugs hide in the corners. The test plan covers at least:

- Two devices edit the same record concurrently and reconverge.
- A device edits offline for 24 hours, then comes online.
- A device deletes a record that another device is editing.
- A device's clock jumps forward by an hour mid-edit (HLC must survive).
- The user uninstalls and reinstalls; local state is rebuilt from the server.
- The server's storage is restored from a backup; clients must reconcile without dropping local-only edits.
- Network drops mid-push; the client retries without duplicating.
- Network drops mid-pull; the client resumes from the last cursor.
- The user signs out and signs in as a different user on the same device.
- A field-level LWW conflict where the timestamps are equal to the millisecond (tie-break by `device_id`).

Each scenario gets an automated test (a unit test for the merge logic, an integration test that simulates two clients) and a manual test for the UI failure mode.

### 8. Choose libraries pragmatically

If the design requires CRDTs and the team is small, do not implement them from scratch. Use:

- **Automerge** for JSON-document-shaped data with rich history.
- **Yjs** for collaborative text and structured data with broad ecosystem support.
- A managed sync product (Realm, Supabase Realtime, PowerSync, ElectricSQL, Firebase Firestore offline) if the team accepts the vendor and the feature set fits.

If the team writes their own protocol, the simplest viable starter is:

- LWW with HLC on individual records.
- Server holds the canonical state and an integer version per record.
- Sync cursor is `(server_version_high_water_mark)`.
- No real CRDT semantics beyond per-field LWW.

This handles 80% of single-user-multi-device cases and gives a clean upgrade path to richer CRDTs later if collaboration arrives.

## Outputs

`design_document` is the structured document covering the seven phases.

`data_model_sketch` is the schema fragments and the sync payload examples.

`test_plan` is the explicit list of scenarios with pass criteria.

## Examples

### Example: shared notes app, small-team-collaborative, free-text + lists

Excerpt from `design_document`:

```
## Problem
Notes are edited by 2-5 collaborators per note. Edits are interleaved
free-text plus structured checklists. Acceptable failure: cosmetic
ordering drift in a long checklist. Unacceptable failure: lost edits
or duplicated checklist items.

## Conflict policy
- Note body: Yjs text CRDT, persisted as a Y.Doc binary.
- Checklist items: Yjs Y.Array of Y.Map, each item with id, text, done.
- Note metadata (title, archived flag): LWW per field with HLC.
- Document deletion: tombstone with 30-day grace; visible-but-greyed
  state for collaborators while the grace window is open.

## Local data model
- table notes(id, doc BLOB, meta JSON, hlc, last_synced_op_id)
- table pending_ops(note_id, op BLOB, hlc, op_id)
- pending_ops cleared once the op_id is acknowledged

## Sync protocol
- HTTPS long-poll with binary frames carrying Y.js update bytes.
- Cursor: server-issued monotonic op_id.
- Reconnection backoff: 1s, 5s, 30s, capped at 60s, plus jitter.

## UI affordances
- Cursor presence shown live for collaborators.
- Sync banner appears if last_synced_op_id is older than 30 s and we
  are connected; suggests retry.
- Conflict UI: not required for body/checklist (CRDT converges).
  Required for metadata (rare): banner asks user to pick title.
```

Excerpt from `test_plan`:

```
1. Two devices edit different paragraphs simultaneously; both see both
   paragraphs after sync.
2. Two devices toggle the same checklist item to opposite states within
   200 ms; the resulting state is deterministic and matches the HLC
   ordering.
3. Device A adds three items; Device B deletes the second one mid-add;
   final list shows A's items 1 and 3 plus B's deletion respected.
4. Device A renames the note while Device B archives it; both changes
   survive (different fields, both LWW).
5. Device A and Device B both rename the note to different titles;
   conflict banner appears on whichever syncs second; user picks.
```

## Limitations

- The skill produces a design, not a working sync engine. Implementation requires careful concurrency and substantial test investment.
- The CRDT library choice has ecosystem and lock-in implications; the skill names options but the team must verify SDK availability for their platforms.
- Encryption at rest, key rotation, and end-to-end encryption are out of scope; flag those as separate workstreams.
- Server design (storage layout, indexing, retention) is touched only where the wire contract demands it; full backend design is a separate exercise.
- Real distributed-systems edge cases (Byzantine clients, malicious servers) are not covered; the design assumes cooperating-but-unreliable parties.

## Sources reviewed

- https://github.com/automerge/automerge
- https://github.com/yjs/yjs
- https://github.com/Kotlin/kmp-production-sample
- https://github.com/android/nowinandroid
- https://github.com/thecodingmachine/react-native-boilerplate
- https://github.com/obytes/react-native-template-obytes
- https://github.com/VeryGoodOpenSource/very_good_templates
