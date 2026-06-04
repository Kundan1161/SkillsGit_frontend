---
id: skillsgit-curated/api-versioning-strategy-architect
version: 1.0.0
name: API Versioning Strategy Architect
description: Design a versioning strategy for an evolving API — selector (URI, header, media type, param), cadence (semver, dated, rolling), deprecation policy with Sunset and Deprecation headers, breaking-change rules, and migration support.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - niche:api-versioning
  - deprecation
  - sunset-header
  - breaking-change
  - migration
  - openapi
  - graphql-evolution
  - api-lifecycle
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - api versioning
  - api version
  - breaking change
  - deprecation policy
  - sunset header
  - Deprecation header
  - dated versioning
  - rolling versions
  - semver api
  - URI versioning
  - header versioning
  - media type versioning
  - graphql evolution
  - schema deprecation
  - migration plan
example_invocations:
  - "We need to introduce a breaking change to our public REST API — design a versioning and migration plan."
  - "Pick a versioning strategy for our new public API; we expect many small additive changes and a few large ones per year."
  - "How should we evolve our GraphQL schema without versioning, and what deprecation discipline do we need?"
inputs:
  - name: api_shape
    type: text
    required: true
    description: REST, GraphQL, gRPC, RPC, or hybrid. Public, partner-only, or internal. Read-heavy vs write-heavy. Whether SDKs are first-party.
  - name: client_population
    type: text
    required: false
    description: Who calls the API — first-party apps, partner integrations, anonymous public, embedded devices. How fast they can upgrade. Whether you control them.
  - name: change_cadence
    type: text
    required: false
    description: How often the API changes — additive monthly, breaking yearly, ad-hoc. Whether the team has the maturity for dated or rolling versioning.
  - name: deprecation_constraints
    type: text
    required: false
    description: Regulatory, contractual, or SLA constraints on how long an old version must run. Whether sunset must be announced at signup.
  - name: existing_versioning
    type: text
    required: false
    description: Anything already in place — version segments in the URL, SDK versions, OpenAPI history, deprecation conventions. The migration starts from here.
outputs:
  - name: versioning_design
    type: markdown
    description: A design document — selector mechanism, cadence model, breaking-change rules, deprecation policy with header contract, dual-stack support, and rollout.
  - name: deprecation_policy
    type: markdown
    description: A standalone deprecation policy ready to publish — minimum support window, Deprecation and Sunset header contract, announcement channels, exception process.
  - name: migration_playbook
    type: markdown
    description: A step-by-step playbook for shipping a breaking change — additive phase, dual-stack window, client migration support, sunset, removal.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# API Versioning Strategy Architect

## When to use

Use this skill when a team is designing a versioning strategy for a public, partner, or internal API, or revising one that has begun to hurt. The output is a coherent choice of version selector, change cadence, deprecation policy, and migration mechanics. The skill is opinionated about which approach fits which problem; it does not commit to a specific framework.

The skill applies to:

- New public APIs that will evolve over years and need a story for change.
- Existing APIs that have accumulated ad-hoc versioning and are about to ship a breaking change.
- Internal APIs that have grown enough clients that breaking changes now require coordination.
- GraphQL schemas where the team needs evolution discipline in place of explicit versions.
- gRPC services with proto evolution rules that must align with consumer pinning policy.

Do not use this skill for:

- One-shot RPC contracts within a tightly coupled monolith where consumers and producers ship together — versioning is overhead there.
- Schema migrations on a database — different problem with different constraints.
- Negotiating wire formats (JSON vs protobuf) — that is a serialization choice, not a versioning one.

## Inputs

- `api_shape` (required) — Determines the available selector mechanisms and the dominant evolution pattern.
- `client_population` — Determines how aggressively breaking changes can be shipped and how long the support window must be.
- `change_cadence` — Determines whether semver, dated, or rolling versions fit the team's flow.
- `deprecation_constraints` — Determines the minimum support window and how sunset must be communicated.
- `existing_versioning` — Constrains the design to a feasible migration from where the API actually is.

## How to apply

The design proceeds top-down: pick the cadence model, pick the selector, write the change rules, define the deprecation policy, then design the migration mechanics.

### 1. Frame the evolution problem

1.1. Three questions decide most of the design:

- **How often does the API change in ways visible to clients?** Once a year is one regime; monthly is another.
- **How fast can clients adopt new versions?** First-party mobile apps move at the pace of app-store reviews; partner integrations move at quarterly cycles; embedded devices may never upgrade.
- **What is the cost of a wrong move?** Breaking an embedded device fleet is a recall; breaking a SaaS integration is a support ticket.

1.2. The version selector is a contract with clients. Once chosen, switching it is itself a breaking change. Design carefully.

1.3. The default posture should be "evolve without breaking when possible". Most changes are additive; reserve versioning for the changes that truly cannot be made additive.

### 2. Pick the cadence model

2.1. **Semver (1.0, 1.1, 2.0)** — version increments tied to compatibility. Strong fit for SDK-shaped APIs and gRPC. Less fit for many small public-API changes; clients balk at upgrading version numbers monthly.

2.2. **Dated versions (2025-04-01)** — each release is identified by date. Clients pin to a date; the server runs many concurrent dates. Each version is a known snapshot of behavior. Strong fit for APIs that ship frequent small breaking changes and want each client to opt into them. The pattern popularized by payment APIs and used by several large platforms.

2.3. **Rolling versions** — like dated, but each new version supersedes the previous on a fixed schedule, with clients automatically promoted unless they pin. A documented migration window separates announcement from auto-promotion.

2.4. **Single-version with continuous evolution** — no versions at all; only additive changes; deprecation removes fields after a sunset window. Native to GraphQL, possible for REST when discipline is high.

2.5. **Heuristic for first pass:**

- Few clients, slow cadence, predictable changes: semver.
- Many clients, frequent small breaking changes, willing to invest in version-translation infrastructure: dated or rolling.
- Strong additive discipline and willingness to maintain backward compatibility forever: continuous evolution.

2.6. The cadence must fit the team's operational maturity. Dated versions require a version-translation layer; promising one without building it is a worse outcome than picking semver.

### 3. Pick the selector

3.1. **URI segment** (`/v1/orders`) — visible, cacheable, easy to route at the edge. The dominant style for public REST. Pathology: clients embed the version in every URL; bumping it is a coordinated rewrite.

3.2. **Header** (`Accept-Version: 2025-04-01` or a custom header) — keeps the URL stable across versions, isolates routing logic. Less discoverable; harder to test from a browser; some CDNs strip unknown headers.

3.3. **Media type** (`Accept: application/vnd.example.v2+json`) — RFC-aligned content negotiation. Powerful but unfamiliar to many clients; many tools treat it awkwardly.

3.4. **Query parameter** (`?api-version=2`) — easy for clients to add ad-hoc, easy to test in a browser. Pollutes URLs; mixes routing with payload. Reasonable for internal or admin APIs.

3.5. **Subdomain** (`v2.api.example.com`) — clean separation, but each version is a separate origin: TLS, DNS, CORS, CDN cache namespaces all multiply.

3.6. **gRPC and protobuf** — the package name carries the version (`example.v1`). The selector is implicit in the generated code. Evolution rules apply at the proto level (field numbers immutable, field renames forbidden, enums extensible only).

3.7. **GraphQL** — there is no selector; the schema evolves. Clients ask for the fields they need. Old fields stay until usage drops to zero. Deprecation is announced via the `@deprecated` directive with a `reason`.

3.8. **Heuristic:**

- Public REST with broad audience: URI segment for major; header or media type for sub-versions within major.
- Partner-only REST: header is fine; less constrained by browser tooling.
- gRPC: package version, no other choice.
- GraphQL: continuous evolution.

3.9. Document the chosen selector in the API reference, including the default version when none is supplied and the error behavior when an unknown version is requested.

### 4. Write the breaking-change rules

4.1. Define **breaking** explicitly. A change is breaking when it can cause a previously valid request or response handling to fail. Concrete examples:

- Removing or renaming a field clients may read.
- Changing the type or shape of a field.
- Tightening a validation rule (rejecting input previously accepted).
- Changing default values that clients rely on.
- Changing pagination semantics.
- Changing authentication scope requirements.
- Changing the error code returned for a given condition.
- Changing the HTTP status code for a given outcome.

4.2. Define **non-breaking** (additive) explicitly. The set is narrower than teams hope:

- Adding a new endpoint.
- Adding a new optional request field.
- Adding a new response field that existing clients ignore.
- Adding a new enum value, **only** if clients are documented to tolerate unknown values.
- Loosening a validation rule (accepting input previously rejected).

4.3. Field-level rules under each shape:

- **JSON REST** — adding fields is safe if clients are documented to ignore unknown ones; many older clients are not. Provide a feature flag or a `fields=` selector if conservative clients need shape stability.
- **Protobuf** — field numbers immutable; field names rename safely on the wire but not in code; enums extensible only by appending unless `unknown_value` is handled.
- **GraphQL** — adding fields and types is always safe; changing a nullable field to non-nullable is breaking; changing return types is breaking; removing fields requires deprecation first.

4.4. Document a **change checklist** — every API change passes through it before merge. Each item answers: is this breaking, what version does it land in, what deprecation is required.

4.5. Automate the check where possible. OpenAPI diff tooling can flag breaking changes between versions; GraphQL schema diff tools can categorize changes as breaking, dangerous, or safe; protobuf has buf-style breaking change detection.

### 5. Define the deprecation policy

5.1. Pick a **minimum support window**. Typical values:

- Internal APIs with monorepo clients: 30 days, sometimes shorter.
- Partner APIs: 6–12 months.
- Public APIs with diverse client base: 12–24 months.
- APIs serving embedded devices or financial integrations: 24–36 months, often longer.

5.2. Pick **announcement channels**. The policy must specify where deprecations appear — the changelog, the API console, an email to each client's contact, response headers on the deprecated path. All four are typical for public APIs; fewer for internal.

5.3. Define the **header contract**. The IETF conventions:

- `Deprecation: @<unix-timestamp>` or `Deprecation: true` — emitted on responses from a deprecated endpoint or version. RFC 9745.
- `Sunset: <HTTP-date>` — the date after which the endpoint will be removed. RFC 8594.
- `Link: <https://example.com/migration>; rel="successor-version"` and `rel="deprecation"` — pointers to the migration guide and a richer deprecation explanation.

5.4. Emit the deprecation signal on **every** response from the deprecated path or version. Clients monitor logs and dashboards; a header on every response is the only reliable signal.

5.5. **Sunset date discipline**: the date is a commitment, not a wish. Move it only forward, never backward, and only with explicit policy.

5.6. **Removal**: at the sunset date, the deprecated path returns a clear error (`410 Gone` with a body pointing to the successor) for a grace period, then is removed entirely. Skipping the 410 phase causes confused integrations.

5.7. **Exception process**: a documented path for a customer to request an extension. Tie extensions to the customer's migration plan; do not extend silently.

5.8. **Announcement timing**: deprecate at least one support window before sunset. A 12-month window means the deprecation announcement and the sunset date are 12 months apart, with the announcement repeated quarterly.

5.9. **Changelog discipline**: every change — additive, breaking, deprecating — is in the changelog with a date, a category, an example, and a migration note for breaking entries. The changelog is the canonical history.

### 6. Design dual-stack and version translation

6.1. When two versions run concurrently, three implementation shapes are common:

- **Independent stacks** — separate code paths per version. Simplest to reason about; cost grows linearly with the number of supported versions.
- **Version translation layer** — one canonical internal model; per-version translators convert requests in and responses out. Cost grows sublinearly; needs investment.
- **Branch-by-version flags** — flags in shared code switch behavior by requested version. Tempting but brittle; flags accrete forever.

6.2. **Recommend the translation layer** when more than two versions will be supported at once. The team that adopts dated versioning without it eventually drowns.

6.3. The translation layer's contract: each version is a directional translation pair — request-in (older to canonical) and response-out (canonical to older). Translations are pure functions; composability of translations across many small versions is the whole point.

6.4. The canonical model is **the latest version** plus any internal-only fields. Older versions are translated outward.

### 7. Plan client migration support

7.1. **Migration guides** — one document per breaking change, with side-by-side examples (old request → new request, old response → new response). Generic prose is not enough; clients want copy-paste examples.

7.2. **Diff tools** — publish a machine-readable diff (OpenAPI changes, GraphQL schema diff, proto diff) so clients can lint their integration against the new version before cutting over.

7.3. **SDK updates** — first-party SDKs should ship a version that supports both the old and new API versions during the dual-stack window. Bump the SDK major when the old API removal lands.

7.4. **Codemod or rewrite tools** — for syntactic migrations (renamed fields, restructured payloads), provide a script. Most clients will not write one themselves; many will simply not migrate without one.

7.5. **Customer-visible dashboards** — show each client which API versions they currently use, when each is sunset, and how many calls per day. Customers cannot migrate what they cannot see.

7.6. **Direct outreach** — for high-value or high-traffic customers, the API team contacts them directly with their specific migration list. The most expensive part of every breaking change is reaching the long tail of clients who do not read announcements.

### 8. Plan the rollout of a breaking change

8.1. **Additive phase** — ship the new shape additively first. Old fields and old endpoints continue to work; new ones are available. Clients can migrate at their pace.

8.2. **Deprecation announcement** — mark old shape as deprecated; emit `Deprecation` and `Sunset` headers; publish migration guide; announce to clients.

8.3. **Dual-stack window** — run old and new in parallel. Monitor usage on the old. Outreach to top users still on it.

8.4. **Sunset** — at the announced date, switch the old path to `410 Gone` for a grace period (typical: 30 days).

8.5. **Removal** — after the grace period, remove the old code path.

8.6. Do not telescope the phases. Each phase exists to give clients a chance to act. A short timeline saves engineering time and costs trust.

### 9. Handle GraphQL specifically

9.1. GraphQL omits the selector entirely. The schema is one. Versioning is replaced by:

- **Additive evolution** — add new fields and types; never remove without deprecation.
- **`@deprecated` directive** — annotate the field or argument with a `reason` and, optionally, a target removal date.
- **Field-usage telemetry** — track how often each field is queried and by which client. Removal is safe only when usage of a deprecated field falls to zero or a known acceptable level.
- **Persistent operation registry** — for first-party clients, a server-known list of allowed queries; the registry shows exactly which queries reference each field.
- **Schema diff in CI** — every PR runs a schema diff; breaking changes are flagged and require sign-off.

9.2. The same deprecation discipline (timeline, announcement, grace period) applies to field removals.

### 10. Handle gRPC and protobuf specifically

10.1. Proto evolution rules:

- Field numbers are immutable.
- Field types may not change.
- Adding fields is safe.
- Renaming a field affects generated code but not the wire format.
- Removing a field: reserve the number with `reserved` to prevent accidental reuse.
- Enum values: append-only; the `0` value is the default and must remain.
- `oneof` cannot be safely modified.

10.2. Package version (`example.v1`) increments on breaking change; the old package continues to be served until sunset.

10.3. Proto-breaking-change tools should run in CI on every change.

### 11. Emit the design

11.1. Lead with the cadence and selector choices and the rationale.

11.2. Include the breaking-change rule list, copy-paste-ready for the team handbook.

11.3. Include the deprecation policy, formatted for publication.

11.4. Include the dual-stack and translation strategy, sized to the version count.

11.5. Include the rollout phases with example timing.

11.6. Include the changelog convention and the announcement-channel list.

### Decision rules and heuristics

- **Additive first, version-bump last.** A breaking change is a failure of design imagination until proven otherwise.
- **One selector, well-documented.** Mixing selectors confuses clients.
- **The cadence must match the team's maturity.** Dated versioning without a translation layer is a debt trap.
- **Deprecation is a date, not a vibe.** Set the date, emit the headers, publish the guide, do the outreach.
- **Visibility beats announcement.** A header on every response and a dashboard for the customer beats an email they did not read.
- **Removal goes through 410.** Skipping it confuses clients who never saw the deprecation.
- **Translate, do not branch.** A version-translation layer scales; per-version branches do not.
- **GraphQL is versionless; the discipline replaces it.** Without the discipline, the schema rots.
- **Proto is forgiving on the wire, strict in code.** Treat the proto file like an API.
- **Document the policy publicly.** Customers plan against your dates only if they trust them.

### Edge cases

- **Embedded devices** — the support window is measured in years. A breaking change may need to coexist with the old version indefinitely until the fleet is replaced.
- **Webhooks** — your service is the client; the receiver's compatibility constraints apply. Send dated payloads pinned at subscription time so receivers do not see surprise breaking changes.
- **SDK pinning** — first-party SDKs that pin a specific API version protect customers from drift but trap them on old versions. Publish a maintained SDK that tracks the latest.
- **Plan-tier-specific shapes** — if enterprise customers get extra fields, those are part of the schema, not a version. Document them.
- **Internal APIs adopted externally** — an internal API used by a partner becomes a public API. Version it accordingly the moment external consumption begins.
- **Long-running operations** — a job that ran under version N may need to emit results under version N even after N is sunset for new requests. Plan the result pipeline.
- **Search and projection endpoints** — `fields=` or similar projection parameters are not a substitute for versioning. They reduce response surface; they do not freeze behavior.

## Inputs

(See frontmatter.)

## Outputs

- `versioning_design` — Selector and cadence, breaking-change rules, dual-stack and translation strategy, rollout sequence.
- `deprecation_policy` — Minimum support window, header contract, announcement channels, sunset and removal steps, exception process.
- `migration_playbook` — Phase-by-phase steps for shipping a breaking change with client migration support.

## Examples

### Worked example

Input excerpt:

> Public REST API for a payments platform. About 5,000 active integrations, ranging from major partners to long-tail self-serve. We add fields monthly and ship a meaningful breaking change once or twice a year. Current state: `/v1/...` URI segment, no formal deprecation policy. We need a versioning model that lets us ship breaking changes safely without forcing every customer to a global migration each time.

Expected output sketch:

- Cadence: dated versions (e.g., `2026-05-14`), with `/v1/...` retained as the URL prefix for stability. New dated versions ship as needed; each is a behavioral snapshot.
- Selector: HTTP header `Api-Version: 2026-05-14`, with a server-side default version pinned per account at signup and overridable per request. URI segment stays at `/v1/` since the team will not move to `/v2/`; segment bumps reserved for catastrophic redesigns.
- Translation layer: one canonical internal model; per-version translators convert requests in and responses out. Each new dated version adds two pure functions.
- Breaking-change rules: documented list (Section 4.1) used as a merge-gate checklist. OpenAPI diff in CI flags breaking changes; merge requires explicit version-bump or remediation.
- Deprecation policy: 12-month minimum window for public versions. Deprecated versions emit `Deprecation: true`, `Sunset: <HTTP-date>`, and `Link: <migration-guide>; rel="deprecation"`. Removal phase is `410 Gone` for 30 days, then removal.
- Announcement: changelog, in-app banner in the developer dashboard, email to account technical contacts, response headers. High-traffic accounts get direct outreach.
- Migration playbook: additive phase (release new shape next to old, default account version unchanged) → deprecation announcement on old shape → 12-month dual-stack → sunset → 30-day 410 grace → removal.
- Client visibility: dashboard shows each account which versions their traffic uses, with a per-version sunset date and a "migration progress" view.
- Internal infrastructure: translation layer, OpenAPI diff in CI, version-pin per account at signup, header-injection support in first-party SDKs.

## Limitations

- The skill produces a strategy from the inputs supplied; calibrating the support window and announcement cadence requires knowledge of the actual customer base.
- It does not implement the version-translation layer; that is engineering work proportional to the API surface.
- It does not address authentication, authorization, or transport changes; those have separate constraints that interact with versioning but are not its core.
- It assumes the team can sustain the discipline (changelog, CI diff, outreach). Without the discipline, no versioning model survives contact with reality.
- Specific RFC numbers, header names, and timing windows reflect current practice and should be checked against the latest published RFCs and platform documentation at adoption time.

## Sources reviewed

- https://github.com/dotnet/aspnet-api-versioning (MIT)
- https://github.com/OAI/OpenAPI-Specification (Apache-2.0)
- https://github.com/graphql/graphql-spec (OWFa 1.0)
- https://github.com/kamranahmedse/design-guide-for-apis (MIT)
- https://github.com/microsoft/api-guidelines (CC-BY-4.0)
- https://github.com/bufbuild/buf (Apache-2.0)
- https://github.com/kamilkisiela/graphql-inspector (MIT)
- https://github.com/Tufin/oasdiff (Apache-2.0)
