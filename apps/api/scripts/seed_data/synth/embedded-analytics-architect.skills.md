---
id: skillsgit-curated/embedded-analytics-architect
version: 1.0.0
name: Embedded Analytics Architect
description: Designs an embedded-analytics surface inside a product — multi-tenant data isolation, row-level security, embed mechanism choice (iframe / SDK / reverse-proxy), authentication flow, performance budget, branding, and lifecycle.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: data
tags: [niche:self-service-bi, embedded-analytics, multi-tenant, row-level-security, sso, performance, sdk, white-label]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  tools_optional: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 9000
trigger_keywords:
  - embedded analytics
  - embedded dashboard
  - white label analytics
  - multi-tenant analytics
  - row level security
  - tenant isolation
  - iframe dashboard
  - SDK analytics
  - JWT embed
  - customer-facing analytics
  - product analytics surface
  - in-app dashboards
  - reverse proxy analytics
example_invocations:
  - "We want to embed dashboards in our SaaS app so customers see only their own data. Design the architecture."
  - "Should we use iframe embedding, an SDK, or a reverse proxy for our customer analytics?"
  - "Plan row-level security for embedded analytics across 5,000 tenants."
  - "How should we handle SSO from our app into the embedded analytics tool?"
inputs:
  - name: product_context
    type: text
    required: true
    description: The host product, the surface where analytics will appear (a page, a tab, a modal), the user types that will see it (end users, account admins, internal staff), and the value proposition (operational insight, billing transparency, benchmarking).
  - name: tenancy_model
    type: choice
    required: true
    description: How customer data is separated today.
    choices: [shared-schema-tenant-column, schema-per-tenant, database-per-tenant, hybrid, no-multi-tenancy-yet]
  - name: scale
    type: text
    required: true
    description: Approximate tenant count, average and largest tenant size in rows, peak concurrent embed sessions, and growth trajectory.
  - name: data_source
    type: text
    required: true
    description: Where the analytics data lives — production OLTP, replicated OLAP store, dedicated warehouse, lakehouse — and how fresh it is.
  - name: branding_requirements
    type: choice
    required: false
    description: How much the embed must look like the host product.
    choices: [full-white-label, host-branded-frame-tool-rendered, dual-branded, tool-branded-acceptable]
  - name: sla_target
    type: choice
    required: false
    description: Service-level target for the embed.
    choices: [best-effort, 99-percent, 99-5-percent, 99-9-percent, 99-95-percent]
outputs:
  - name: tenancy_and_security_design
    type: markdown
    description: How tenant isolation is enforced at the data layer, the analytics layer, and the network layer; the row-level-security policy; the authentication and token flow.
  - name: embed_mechanism_recommendation
    type: markdown
    description: Iframe, SDK, or reverse proxy, with the reasoning and the trade-offs of the unchosen options.
  - name: performance_design
    type: markdown
    description: Performance budget, caching layout, pre-aggregation strategy, and the load behavior at peak.
  - name: branding_and_ux
    type: markdown
    description: How the embed reads as part of the host product — theming, interactive surface, error states, empty states.
  - name: lifecycle_and_operations
    type: markdown
    description: Release, version pinning, dashboard updates without breaking embedded customers, observability, and the support model.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

## When to use

Invoke this skill when a team is putting analytics inside a customer-facing product — not for internal employees, but for the product's end users — and needs an architecture that holds up across hundreds or thousands of tenants. Typical situations:

- A SaaS product wants to expose dashboards to its customers as a paid feature or as a transparency surface.
- A platform that already has a working internal BI deployment is being asked to surface a subset of those dashboards to external users and must rebuild the security model.
- A product team is deciding between building charts in the application framework versus embedding a BI tool's rendering layer.
- A regulated business needs an isolation design defensible to customer audits before shipping any embed.
- Performance is suffering: every customer's embed is hitting the warehouse on every page load, and the warehouse bill is growing faster than revenue.

Do not invoke this skill for internal-only dashboards (use the self-service-bi-rollout-architect skill). Do not invoke it for picking a BI tool — embed mechanism is a smaller decision than the tool choice. Do not invoke it for designing the dashboard itself (use the dashboard-architect skill).

## How to apply

The methodology treats embedded analytics as a product feature with three hard constraints — security, performance, and lifecycle — and a fourth soft one, branding. Get any of the hard constraints wrong and the feature ships with a liability. The decisions interact: a security model that requires a per-request authorization check changes the cache layout, which changes the performance budget, which changes the embed mechanism.

### 1. Anchor on the customer-facing contract

1. **State who the reader is.** End users, customer admins, the customer's customers (a second-degree case that changes everything), or internal staff. The reader's identity drives every isolation decision downstream.
2. **State the data scope.** What rows belong to a given embed session — by tenant, by user within the tenant, by sub-account. The unit of isolation is rarely "tenant"; it is usually "tenant + role + sometimes user."
3. **State the freshness contract.** A billing dashboard refreshed nightly is a different system from a real-time operational embed. The customer's expectation is set by what they see, not by what is documented.
4. **State the durability contract.** When the host product changes, when the BI tool upgrades, when the underlying data model changes — what is the customer entitled to see and not see?
5. **State the SLA.** Best-effort, 99%, 99.9% — each tier changes the operational requirements substantially. A 99.95% target for a customer-facing surface means staffed on-call, observability, and a degradation strategy.

### 2. Choose the tenancy enforcement layer

6. **Identify where isolation is enforced.** Three candidates: the application layer (the host product issues a per-tenant token and the analytics tool filters on it), the database layer (row-level rules on the source), or both.
7. **Prefer enforcement at the database layer.** A row-level rule at the source — using the database's native row-security feature or an equivalent — fails closed. If the analytics tool is misconfigured, the database still refuses to return rows that don't match the policy.
8. **Treat application-layer filtering as belt-and-suspenders, not the only defense.** A signed token passed to the BI tool that drives a filter is convenient but not sufficient; it relies on the analytics tool's correctness for security.
9. **Map tenant identity to the database session.** Whatever the data tenancy model — shared schema with a tenant column, schema-per-tenant, database-per-tenant — there must be a way for the database to know which tenant is being served on each query. Without that, no row-level policy is enforceable.
10. **Document the failure mode.** What happens if the token is missing or malformed? The system must return zero rows, not all rows. The default failure must be "no data" rather than "wrong data."
11. **Audit the cardinality of the tenancy attribute.** Five tenants are easy; fifty thousand stresses indexing strategies and policy-engine performance. Plan for 10x the current count.
12. **Reject silent cross-tenant aggregates.** If a product feature requires cross-tenant numbers (benchmarking, "you vs. median customer"), that aggregate must be computed in a place that no end-user query can directly access, and surfaced as a pre-computed, anonymized series.

### 3. Design the authentication and authorization flow

13. **Pick the token format.** A signed token (JWT or equivalent) issued by the host product, carrying the tenant identifier, the user role, and a short expiry, is the workhorse. Long-lived API keys are a security smell for end-user surfaces.
14. **Set the expiry short.** A token valid for an hour is far less dangerous than one valid for a week. Refresh on the host application's session boundary.
15. **Include a session identifier in the token** so a per-session audit trail is possible. The BI tool's logs must be joinable back to the host application's session log.
16. **Sign the token with a key the BI tool also holds.** Rotate the key on a schedule; design for rotation to be a non-incident.
17. **Validate the token on every request, not just at session start.** A session that started valid can be revoked; the renderer must respect revocation.
18. **Decide what the BI tool does with the token claims.** Common pattern: claims are bound to filter parameters that the row-level policy reads. The renderer cannot bypass them because the database enforces them.
19. **Plan an internal-staff path that does not collide with the customer path.** An internal employee debugging an embed has a different identity model; do not let them inherit a customer's permissions accidentally.
20. **Plan an audit trail.** Who saw which embed, for which tenant, at what time, with what filters. Customers will ask; auditors will demand.

### 4. Pick the embed mechanism

21. **Three candidate mechanisms.** Iframe with a signed URL; an SDK that renders into the host page; a reverse proxy that fronts the BI tool with the host product's session.
22. **Iframe with a signed URL** is the lowest-effort option. The host product mints a short-lived signed URL; the BI tool renders into an iframe; events between host and iframe go over postMessage. Pros: minimal integration, full BI-tool feature surface, isolated styling. Cons: limited styling control, cross-origin friction (cookies, postMessage), and a hard ceiling on how "embedded" it can feel.
23. **An SDK that renders into the host page** is the deepest integration. The BI tool provides a client library; the host application calls it with a token; the library renders charts using host-page DOM. Pros: native styling, easier interaction with host UI, no iframe friction. Cons: more code to maintain on both sides, version-coupling between host and SDK, and a larger attack surface inside the host page.
24. **A reverse proxy** sits the host product in front of the BI tool's web UI, forwarding authenticated requests. Pros: the embed looks like the host domain, host cookies flow naturally. Cons: an entire web app proxied is a wide surface — admin pages, exports, anything the BI tool exposes is now reachable; allowlist routes carefully.
25. **Pick iframe first when integration effort is low and branding tolerance is "host-branded frame, tool-rendered."** Most embedded-analytics deployments succeed with iframes.
26. **Pick SDK when the embed must feel native and the host product is a single-page application with capacity to maintain the integration.** Expect to budget engineering time for keeping the SDK current.
27. **Pick reverse proxy only when iframe and SDK are both ruled out** and the operations team can manage the additional surface. The proxy is also useful when the BI tool's own URL must not be reachable from the public internet at all.
28. **Plan for the embed mechanism to outlast the BI tool.** Wrap whichever choice in an internal interface (a host-side component, a server-side endpoint) so swapping the underlying tool does not require a host-product redesign.

### 5. Size the performance budget

29. **Pick a target time to first useful pixel.** A widget embedded in a settings page might tolerate 3 seconds; a panel that loads on every dashboard view of the host product must be sub-second or it harms the host product's perceived speed.
30. **Account for the cold case.** Cache misses, just-deployed customers, the first session of the day. The cold case is what customers complain about; design for it.
31. **Decide where charts are computed.** Three layers: in the warehouse on each request, in a pre-aggregated cube refreshed on a schedule, or in a per-tenant materialized cache. Each is appropriate at different scales.
32. **Pre-aggregate when the cardinality of "what end-users will ask" is bounded.** Most embedded analytics is bounded — five charts, a handful of filter combinations. A pre-aggregate by tenant by day is cheap to maintain and very fast to serve.
33. **Cache at the panel level, keyed by tenant + filter + period.** A cache hit returns instantly; a miss runs the query and populates the cache. Set the time-to-live to the freshness contract, not longer.
34. **Plan for the thundering herd.** A nightly refresh that invalidates every tenant's cache at once leads to a stampede when the morning traffic arrives. Stagger invalidation or warm caches in advance.
35. **Plan for the largest tenant.** A 99th-percentile tenant with ten times the rows of the median needs special handling — separate compute, longer time-to-live, or a smaller default filter range.
36. **Plan for the busiest hour.** Customer-facing analytics has a daily traffic shape (morning peaks for many businesses). Design for the peak, not the median.
37. **Budget the per-tenant cost.** A pricing pattern is: dollars per active tenant per month. Multiply expected query cost, cache cost, and tool-license cost; if the per-tenant cost exceeds the per-tenant revenue contribution from the feature, the feature is wrongly designed.

### 6. Brand and shape the embed

38. **Match the host product's typography and color tokens.** A foreign-feeling embed is read as "third-party widget" rather than as a host feature. Even subtle mismatches (a different gray, a wrong heading font) signal "not really part of the product."
39. **Strip the BI tool's chrome.** Logos, default headers, "powered by" footers — disable them if the contract allows. Be sure your license permits white-labeling at the desired branding tier.
40. **Decide the interactivity surface.** Can the customer change the time range? Apply filters? Drill down? Export? Each capability is a product decision with implications for security (export bypasses any row-redaction policy) and performance (drill-down may run unbounded queries).
41. **Design the empty state.** A brand-new customer with no data should see a helpful "no data yet, here is how it gets here" message — not a blank chart that looks broken.
42. **Design the error state.** When a query fails, the embed must say "this view is temporarily unavailable" rather than show a stale or wrong number. Silent error in customer-facing analytics is a trust failure.
43. **Localize numbers, dates, and currency.** Customers in different regions see different formats; the embed must honor the host product's locale.
44. **Plan responsive layout.** The embed must work in the smallest viewport the host product supports. A dashboard designed for 1440px desktop and dropped into a 375px mobile panel looks broken.

### 7. Plan the lifecycle

45. **Version-pin embedded content.** Customers should not see a dashboard change without notice. Treat embedded dashboards like API endpoints — versioned, with deprecation timelines.
46. **Separate authoring from publishing.** A change to an embedded dashboard goes through review, runs in a staging tenant, then publishes to production. Authoring directly in production is how customers wake up to broken charts.
47. **Provide a staging tenant.** A safe place to verify changes before they affect real customers. Without it, the only test bed is a real customer.
48. **Plan for BI-tool version upgrades.** The tool will release new versions. Test the embed against each release before upgrading; pin to a version range; have a rollback path.
49. **Plan for data-model migrations.** When the underlying tables change, the embedded dashboard's queries must change in lockstep. A migration that doesn't include the embedded queries produces a silent break.
50. **Decide the support model.** Customer-facing support tickets land on the host product's support team; the data team is on the back end. Triage rules must route between them quickly. A ticket sitting in the wrong queue is a churn risk.
51. **Decide the on-call posture.** A 99.9% target for a customer-facing surface requires named on-call for the embed path: BI tool, network path, source database, identity service. Set escalation paths and run a drill.
52. **Observability for the embed path.** Per-tenant load time, error rate, query cost. Without these, regressions go unnoticed until customers complain.
53. **Build a kill switch.** A way to disable the embed for a single tenant or globally without a deploy. When something goes wrong, the ability to stop showing the data is itself a safety feature.

### 8. Compose the deliverable

54. **Lead with the tenancy and security design.** This is the load-bearing decision; everything else builds on it. Include the row-level policy approach, the token flow, the audit trail.
55. **State the embed mechanism choice with explicit trade-offs.** Acknowledge what the customer loses by not picking the other two.
56. **Lay out the performance design.** Where charts are computed, the cache layout, the cold-case behavior, the worst-tenant handling.
57. **Sketch the branding and UX.** Theming, interactivity surface, empty and error states, responsive behavior, localization.
58. **Sketch the lifecycle and operations plan.** Version pinning, staging, observability, on-call, kill switch.
59. **State the assumptions.** If the user did not state SLA, tenant count, freshness contract, or branding tier, name the assumption made for each.
60. **Estimate the per-tenant cost.** A rough order-of-magnitude is sufficient; surfacing it forces the conversation about whether the feature is economically sound.

### 9. Self-check before responding

61. **Confirm row-level isolation is enforced at the database, not only at the application.** A design that only enforces at the application is a design with a silent breach risk.
62. **Confirm the default failure mode is "no data," not "wrong data."** Every code path must close on this default.
63. **Confirm the embed mechanism's trade-offs were stated explicitly.** A recommendation without a trade-off is a recommendation that hides its costs.
64. **Confirm the cold-case performance is acceptable.** A warm-case-only design fails on Monday mornings.
65. **Confirm the kill switch exists.** Customer-facing systems need a way to stop the bleeding.

## Inputs

- Product context: host product, surface, reader type, value proposition.
- Tenancy model.
- Scale: tenant count, sizes, concurrent sessions.
- Data source and freshness.
- Optional: branding requirements, SLA target.

## Outputs

- Tenancy-and-security design with row-level policy and token flow.
- Embed mechanism recommendation with trade-offs.
- Performance design with cache layout and worst-case handling.
- Branding and UX guidance.
- Lifecycle and operations plan.

## Examples

**Example invocation**

> "We are a SaaS analytics product with 3,000 tenants, shared-schema multi-tenancy (tenant_id column on every table), in a cloud warehouse. We want to embed three dashboards inside the customer-facing app — usage, billing, and benchmarking. Customer admins and end users will see them. Branding must be fully white-label. We want a 99.9% SLA. Median tenant has 200K rows; largest has 50M."

**Expected high-level output**

Tenancy and security: enforce at the database layer using row-level policy keyed by tenant_id. The host product mints a JWT carrying tenant_id, user_id, role, and a 1-hour expiry, signed with a key the BI tool holds (rotated quarterly). The BI tool passes the claims as filter parameters; the warehouse policy applies them. Default failure: no rows. Audit trail logged per session, joinable to host application logs. Benchmarking aggregates are pre-computed in a separate schema with no row-level access from end-user paths, and surfaced as anonymized series.

Embed mechanism: iframe with signed URL. Iframe wins because the integration effort is low, the BI tool's interactive surface is needed, and the styling requirements can be met by a host-product theme applied to the BI tool's renderer. SDK was considered but rejected: the host product is multi-platform and an SDK would multiply integration work. Reverse proxy was rejected: too wide a surface and harder to operate.

Performance: panels pre-aggregated by tenant by day for usage and billing; benchmarking served from a daily-refreshed anonymized series. Per-panel cache, keyed by tenant + filter + period, TTL 1 hour. Cold case: sub-2-second first paint via warm-on-deploy job that pre-populates caches for tenants with > 1 session per day. Largest tenants get a separate compute lane. Stagger nightly refresh across 2-hour windows. Peak Monday morning sized for 5x median load.

Branding: full white-label per license. Host typography and color tokens applied. Empty state: helpful onboarding when a brand-new customer has no data. Error state: "temporarily unavailable" with a retry. Locale honored.

Lifecycle: version-pinned dashboards. Staging tenant for pre-publish validation. BI tool version upgrades on a tested-then-promoted path with documented rollback. Observability per tenant for load time and error rate. Named on-call for the embed path. Kill switch per tenant and global.

Per-tenant cost estimate: warehouse query cost ~$0.40/month/tenant (pre-aggregated, cached), BI tool license per active session ~$0.20/month/tenant, infrastructure overhead ~$0.10/month/tenant. Total ~$0.70/month/tenant. Feature pricing must cover this with margin.

## Limitations

- The methodology covers architecture, not the BI tool's specific embed APIs. Once the tool is chosen, its embedding documentation is required to wire up the token flow and theming.
- Row-level policy syntax varies by database. The skill specifies "enforce at the database" but the exact policy expression is database-specific.
- Per-tenant cost estimates depend on workload shape and pricing; the skill produces order-of-magnitude, not exact numbers.
- Regulated data (PHI, regulated financial data) requires additional controls (encryption-at-rest claims, key separation, audit retention) that this skill flags but does not fully enumerate.
- The design assumes the customer-facing surface is read-only. Write-back from an embedded analytics surface (where end users edit underlying data through the embed) is out of scope and requires a different security model.

## Sources reviewed

Methodology synthesized across the following projects and public documentation. License tags reflect each project's stated terms at the time of review. No prose, code, or branded terminology is copied; the design vocabulary above is original.

- https://github.com/metabase/metabase — AGPL-3.0 (community) + proprietary (commercial). Read; cited for signed-URL embed and per-tenant-isolation patterns.
- https://github.com/apache/superset — Apache-2.0. Read; cited for guest-token and dataset-row-policy patterns.
- https://github.com/cube-js/cube — Apache-2.0 (backend) + MIT (client). Read; cited for headless-semantic-layer-with-tenant-context and pre-aggregation patterns.
- https://github.com/lightdash/lightdash — MIT + proprietary. Read; cited for token-based embed patterns.
- LookML / Looker embedded documentation (Google Cloud, proprietary). Read only; cited generically for signed-embed and user-attribute-driven access patterns.
- https://github.com/PostgREST/postgrest — MIT. Read; cited for row-level-security-enforced-at-database patterns.
- PostgreSQL row-security documentation (PostgreSQL license, open source). Read; cited for database-layer policy enforcement.
