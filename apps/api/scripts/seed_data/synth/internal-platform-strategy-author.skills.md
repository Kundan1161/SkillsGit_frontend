---
id: skillsgit-curated/internal-platform-strategy-author
version: 1.0.0
name: Internal Platform Strategy Author
description: Define the scope, golden paths, and team-topology shape of an internal developer platform so it accelerates product teams without becoming a bottleneck.
authors:
  - name: Wave-3 Platform Synth
    handle: wave3-platform
    role: author
category: engineering
tags:
  - niche:platform-engineering
  - internal-developer-platform
  - golden-paths
  - paved-roads
  - team-topologies
  - self-service
  - developer-experience
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - gpt-4o
    - gpt-4.1
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7000
trigger_keywords:
  - internal developer platform
  - IDP
  - platform engineering
  - golden path
  - paved road
  - self-service platform
  - platform as a product
  - team topologies
  - platform team
  - developer portal scope
example_invocations:
  - "We're standing up a platform team — what should we own and what should we leave to product teams?"
  - "Help me draft a golden-path catalog for our 80-engineer org."
  - "Our platform feels like a bottleneck. How do we re-scope it?"
  - "What's the right team topology for our IDP rollout?"
inputs:
  - name: org_context
    type: text
    required: true
    description: Org size, number of product teams, current pain points, cloud footprint, regulated industry yes/no.
  - name: current_state
    type: text
    required: true
    description: What exists today (CI, IaC, K8s, portals, ad-hoc scripts) and who maintains each piece.
  - name: top_friction
    type: text
    required: false
    description: The two or three most-quoted developer complaints (e.g. "spinning up a new service takes two weeks").
  - name: constraints
    type: text
    required: false
    description: Headcount available for the platform team, budget ceilings, regulatory must-haves, mandatory tooling.
outputs:
  - name: platform_strategy
    type: markdown
    description: A scoped strategy document with golden-path catalog, ownership boundaries, team-topology recommendation, and 90-day execution plan.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Internal Platform Strategy Author

## When to use

Use this skill when an engineering leader, platform lead, or staff engineer is about to make (or correct) a foundational decision about an **Internal Developer Platform (IDP)**: what to centralize, what to leave to product teams, which "golden paths" to ship first, and how to staff the platform team so it does not become a ticket-driven bottleneck.

It is the **strategy and scope** skill — it does **not** design the service catalog (see `service-catalog-architect`), measure outcomes (see `developer-experience-metrics-designer`), or write specific scaffolds (see `template-and-paved-road-author`). Use this skill *before* those, or any time the platform's scope is being debated.

Trigger on phrases like:

- "internal developer platform" / "IDP" / "developer platform"
- "platform engineering team" / "platform as a product"
- "golden path" / "paved road" / "happy path"
- "self-service infrastructure"
- "team topologies for platform"
- "platform team is a bottleneck"
- "what should the platform own"

Do **not** trigger when the question is purely about Kubernetes, CI/CD vendor choice, or a single tool — those are tactical and have their own skills. Do **not** trigger when "platform" means a customer-facing product platform; this skill is internal-only.

## How to apply

Walk the user through five decisions, in order. Refuse to skip step 1 — most failed platforms skip it.

### 1. Establish the platform's product mission

The platform is a **product**, and product teams are its customers. Ask:

- Who is the **primary customer**? Application developers? SREs? Data engineers? ML engineers? Be specific; "everyone" is the wrong answer.
- What **outcomes** are you optimizing for? Pick at most three from: time-to-first-deploy, change-failure-rate, deploy-frequency, MTTR, security-baseline coverage, cloud-cost discipline, regulatory audit-readiness. More than three and you have no strategy.
- What is the **anti-goal**? Common ones: "we are not building a multi-tenant PaaS", "we are not abstracting Kubernetes", "we are not owning prod incidents for product teams".
- What's the **commitment cadence**? Treat it like a product: roadmap, releases, deprecations announced 1+ quarter ahead.

If the user can't answer these, stop and help them answer before continuing — the rest is wasted otherwise.

### 2. Scope: what to centralize vs leave to product teams

Use the **"thin platform" heuristic**: centralize only what (a) is undifferentiated heavy lifting AND (b) benefits from a single org-wide implementation. Everything else stays with product teams.

| Centralize (platform owns)            | Leave to product teams                   |
| ------------------------------------- | ---------------------------------------- |
| Identity, secrets, network policy     | Business logic, domain modeling          |
| CI runners, base images, SBOM scan    | Service-internal libraries               |
| Deploy mechanism (e.g. Argo CD)       | Per-service release cadence              |
| Observability pipeline (logs/metrics) | Service-specific dashboards & SLOs       |
| Golden-path templates                 | Forks/divergence from templates          |
| Cost allocation tagging               | Per-feature cost optimization            |
| Compliance baselines                  | Compliance-specific business workflows   |

Common failure modes to call out:

- **Over-centralization** ("the platform team owns SLOs"): becomes a queue; product teams disengage from reliability.
- **Under-centralization** ("each team picks their own deployer"): no consistency, no leverage, security drift.
- **Leaky abstraction trap**: hiding Kubernetes behind a "simple" wrapper that breaks the moment a team needs `livenessProbe` tuning. **Prefer thin, transparent abstractions over thick magical ones.** Users should be able to read the generated YAML.

Recommend: **start with golden paths, not full abstractions**. A golden path is an opinionated, supported route through existing primitives — not a wrapper that hides them.

### 3. Draft a golden-path catalog (the heart of the strategy)

A **golden path** = the supported, documented, paved way to do one thing. Each golden path has: trigger ("when do I use this?"), template, owner, support SLA, and an explicit "off-path" escape hatch.

Recommend starting with **three to five paths**, no more. Common high-leverage paths:

1. **New stateless service** — scaffold, CI, deploy, observability, on-call rotation in one templated repo.
2. **New scheduled job / cron** — same, but for batch workloads.
3. **New data pipeline** — orchestrator template, lineage, ownership, retention.
4. **New ML model serving endpoint** — model registry pointer, GPU scheduling, scaling rules.
5. **Add an external integration** — secrets pattern, retry/timeout defaults, allow-list registration.

Anti-paths (worth listing explicitly so teams know they're off-path):

- "Run your own Postgres on a VM" — point to the managed-DB golden path.
- "Build your own auth" — point to the SSO/OIDC golden path.

For each path, ask the user: who owns it, what's the upgrade story when the template changes, and how do non-conforming services get migrated? Without those answers, golden paths rot.

### 4. Pick a team topology

Map to **Team Topologies** patterns (Skelton & Pais):

- **Platform team** — builds and runs the IDP. Customer is product teams. Size: ~1 platform engineer per 6-10 product engineers as a starting ratio; below that you're under-investing, above that you're building features no one asked for.
- **Enabling team** — short-term consulting embed; helps product teams adopt new practices. Pair with platform when introducing a new golden path.
- **Stream-aligned team** — product team consuming the platform.
- **Complicated-subsystem team** — owns a deep specialty (e.g. data infra, ML infra) that the platform team exposes via a thin interface.

Anti-patterns to flag:

- **Platform team = ticket queue**: structural smell — you've built a service org, not a product. Fix with self-service.
- **One mega-platform team for everything**: split when you cross ~12-15 platform engineers; create sub-platforms (e.g. "delivery platform", "data platform") each with its own product mission.
- **No customer feedback loop**: the platform team has no product-manager equivalent and no quarterly customer survey. Add one.

### 5. Sequencing — a 90-day plan

Recommend the user start narrow. A realistic first-90-days arc:

1. **Days 0-15** — pick one primary customer team, run 5 listening interviews, pick **one** golden path to deliver end-to-end, set up the lightweight metric baseline (lead time for changes, time-to-first-deploy).
2. **Days 15-45** — ship golden path v0 to that one team; instrument adoption; explicitly *do not* generalize yet.
3. **Days 45-75** — onboard 2-3 more teams; capture friction; write the second golden path only after the first has 3+ adopters.
4. **Days 75-90** — publish the catalog, the team-topologies diagram, the SLA, and the first "deprecation" of an off-path pattern. Announce the platform as a product.

Refuse to recommend a "big bang" rollout. The strongest signal a platform is failing is that adoption is mandated rather than chosen.

### Cross-cutting principles to weave into the strategy

- **Self-service over service**: every ticket the platform team handles repeatedly is a missing feature.
- **Thinnest abstractions that meet the use case**: prefer composable primitives over wrappers.
- **Documented escape hatches**: every paved road must have a clear "I need to go off-road" exit; otherwise teams fork silently.
- **Versioning and deprecation in public**: templates and APIs follow semver; breaking changes get N+1 quarter notice.
- **Cost transparency**: the platform reports its own cost-per-team back to the org so it doesn't look like a free good.

## Inputs

- **org_context** (required): "We're a 250-engineer SaaS, ~30 product teams, AWS + a little GCP, SOC 2 + HIPAA, mostly Go and Python services."
- **current_state** (required): describe each existing piece (CI tool, IaC tool, deployer, portal, runtime, secrets manager) and its current owner — even if the owner is "nobody, it just exists".
- **top_friction** (optional): the two or three quotes you hear most from product teams.
- **constraints** (optional): platform team headcount available, budget, regulatory must-haves, any vendor lock-ins.

## Outputs

A markdown strategy with this shape:

1. **Platform mission** — one paragraph, including primary customer, three outcomes, and one explicit anti-goal.
2. **Scope table** — what's centralized, what's left to product teams, with named owners.
3. **Golden-path catalog (v1)** — 3-5 paths, each with trigger, template owner, SLA, off-path escape hatch.
4. **Team topology** — recommended structure with a sizing rationale and adjacent enabling-team plays.
5. **90-day plan** — concrete deliverables per 2-week increment.
6. **Risks and anti-patterns to watch** — tailored to the user's stated current state.

## Examples

> "We're 80 engineers, 10 product teams, on AWS EKS. Today everyone writes their own Helm charts and we have three different CI tools. New services take ~3 weeks to reach prod."

Recommendation: primary customer = service-owning product teams. Outcomes: time-to-first-deploy < 1 day, deploy-frequency 1+/day/team, security-baseline coverage 100% of new services. Anti-goal: not abstracting Kubernetes. First two golden paths: (a) new stateless Go/Python service, (b) standard Helm chart with embedded observability and security defaults. Team topology: 6-person platform team (≈1:13, slightly thin — staff toward 8 within 6 months), one enabling team rotating across product teams. 90-day plan focuses on consolidating to one CI, one deployer (Argo CD), one chart library; explicitly defer service-catalog work to Q2.

> "We're 500 engineers, the platform team owns deploy, CI, K8s, observability, secrets, and on-call for shared services. We're getting >300 tickets/month."

Diagnosis: this isn't a platform, it's a managed-service org. Strategy is **deflection through self-service**, not adding headcount. Recommend: (1) audit the top 20 ticket types — they map to your missing self-service features; (2) split into sub-platforms (delivery, data, observability) each with a product manager; (3) make on-call for shared services co-owned with the consumers (you operate the runway, they fly the plane); (4) introduce a quarterly "platform roadmap" review with product team leads. Expect ticket volume to fall 40-60% within two quarters once 3-5 of the top ticket types are self-serviced.

> "We're a 30-engineer startup. Our 'platform' is two staff engineers and a Notion page."

Push back on building an IDP yet. At this size you have a **paved path**, not a platform. Pick one templated GitHub repo with CI, deploy, monitoring wired in; pick managed services aggressively (managed Postgres, managed K8s, managed observability); revisit "do we need a platform team?" at ~75 engineers or when service count exceeds 25.

## Limitations

- This skill is strategic, not technical. It does not pick specific tools (Backstage vs Port, Argo CD vs Flux, etc.).
- It assumes the org has a coherent engineering function. For multi-business-unit conglomerates, each BU may need its own platform strategy.
- Sizing ratios (e.g. 1:6-1:10 platform-to-product) are heuristics from the public industry literature, not laws. Adjust for tooling maturity and regulatory load.
- It does not address build-vs-buy for the platform itself. Pair with vendor-evaluation skills.
- For pure SRE-led platforms (reliability as the only goal), this skill's "platform as product" framing is over-engineered.

## Sources

- https://github.com/backstage/backstage
- https://github.com/cnoe-io/idpbuilder
- https://github.com/syntasso/kratix
- https://github.com/score-spec/score-compose
- https://github.com/crossplane/crossplane
- https://github.com/argoproj/argo-cd
- https://github.com/cnoe-io/reference-implementation-aws
