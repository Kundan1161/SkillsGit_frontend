---
id: skillsgit-curated/feature-flag-strategy
version: 1.0.0
name: Feature Flag Strategy
description: Recommend a feature-flag taxonomy and lifecycle — release vs. experiment vs. permission vs. operational flags — with naming, ownership, debt management, and kill-switch design.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: marketing
tags: [niche:conversion-rate-optimization, feature-flags, experimentation, release-management, kill-switch, technical-debt, governance, rollout]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - feature flag
  - feature flags
  - feature toggle
  - flag taxonomy
  - kill switch
  - dark launch
  - canary rollout
  - flag debt
  - flag lifecycle
  - release flag
  - experiment flag
  - permission flag
  - operational flag
  - rollout strategy
example_invocations:
  - "We have 300 feature flags and most are stale. How should we clean this up?"
  - "Design a flag taxonomy for our team — we keep mixing experiments and releases."
  - "What kill switches should a payments service have, and who owns them?"
  - "How do we prevent flag debt from accumulating again?"
  - "Help me write the lifecycle policy for our feature-flag service."
inputs:
  - name: current_state
    type: text
    required: true
    description: What flags exist today (rough count and categories if known), what platform manages them, who creates and deletes them, and what problems the team is feeling — debt, surprises, governance gaps, audit failures.
  - name: organization_size
    type: text
    required: true
    description: Engineering team size, number of services, deployment cadence, and whether the company has formal change management, SOC 2, or regulated workloads.
  - name: platform
    type: choice
    required: false
    description: The flag platform in use or planned. Affects what is possible without custom work.
    choices: [growthbook, unleash, openfeature, in-house, multiple, undecided]
  - name: priorities
    type: text
    required: false
    description: What the team most wants to fix — debt cleanup, faster experimentation, safer releases, regulatory audit-readiness, kill-switch coverage, developer ergonomics.
  - name: constraints
    type: text
    required: false
    description: Limits the recommendation must respect — language stacks, multi-region requirements, edge-of-network rendering, mobile app store update cadence, on-prem deploys.
outputs:
  - name: taxonomy_and_policy
    type: markdown
    description: A taxonomy of flag types with definitions, examples, naming conventions, ownership, expected lifetime, and review gates; a lifecycle policy from creation to retirement; and a kill-switch register pattern.
  - name: cleanup_plan
    type: markdown
    description: A staged plan to address current flag debt with weekly milestones, exit criteria, owner roles, and a "do not regress" measurement loop.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Feature Flag Strategy

## When to use

Use this skill when a team or organization has accumulated flags faster than it has retired them, when releases and experiments are tangled in the same flag types, when an audit revealed flags with no owner and no lifecycle, when an outage was caused or worsened by a flag in an unexpected state, or when a new flag platform is being introduced and the question "what counts as a good flag" needs a concrete answer.

The skill works for engineering organizations of any size that have moved past the "few hardcoded toggles" stage and now operate at hundreds-to-thousands of flag scale. It applies equally to organizations running an open-source flag platform, a vendor-managed service, or a homegrown system. The deliverable is a taxonomy and a lifecycle, not a tool selection — tooling is downstream of policy.

Skip the skill when the question is which platform to buy (that is a separate evaluation), when the team has fewer than ten flags and no debt (the policy is overhead it does not need yet), or when the request is for one-off operational guidance on a specific incident (write the incident note instead).

## How to apply

1. **Open with the four flag types.** The convergent industry pattern across modern flag platforms recognizes four distinct flag categories with different lifetimes, owners, and audit needs. (a) Release flags — short-lived, owned by the shipping engineer, retired within weeks of full ramp. (b) Experiment flags — short-lived, owned by the experiment driver, retired at result-confirmation. (c) Permission flags — long-lived, owned by the product or platform team, retired only on entitlement model change. (d) Operational flags — long-lived, owned by the on-call rotation or SRE, retired only on capability deprecation. Mixing the types under a single flag is the most common defect; the rest of the policy depends on separating them.
2. **Define each type with a precise contract.** For each type, state the purpose, the typical lifetime, the owner role, the default rollout shape, the analytics requirement, and the retirement trigger. Release flag: ship code dark; lifetime 1–6 weeks; owner is the shipping engineer; rollout is canary then 100%; analytics is regression watch; retired when at 100% for two weeks with no rollback signals. Experiment flag: gate an A/B test; lifetime equal to the test duration plus a short observation window; owner is the experiment driver; rollout is the assignment function; analytics is the readout; retired when the readout is signed and the variant is either baked in or removed. Permission flag: gate access to a feature by plan, role, account, or compliance posture; lifetime is years; owner is the product team that owns the feature; rollout is a rule, not a percentage; analytics is usage and conversion; retired only when the entitlement model changes. Operational flag (kill switch, traffic shaper, dependency toggle): lifetime is the life of the capability; owner is the on-call rotation; rollout is binary or graded; analytics is whatever drives the flip decision; retired only on capability deprecation. Make these contracts the source of truth.
3. **Forbid type-mixing under a single flag.** A release flag is not used to gate access to a feature on plan basis later. An experiment flag is not converted to a permission flag at the conclusion of the test. An operational kill switch is not used to ship a feature dark for two months. When a flag has done its job in one category, retire it and create a new flag in the other category if the use case persists. Type-mixing is how flag debt accumulates and how on-call surprises happen.
4. **Establish a naming convention.** The flag name encodes its type, its surface, and its purpose. A workable pattern: `{type}_{surface}_{purpose}_{owner-team}`. Examples: `release_checkout_apple-pay-button_payments`, `experiment_pricing-page_hero-rewrite_growth`, `permission_account_advanced-analytics_product`, `operational_inference_gpu-fallback_ml-platform`. The leading `type` token makes audit reports trivial, the trailing `owner-team` token makes ownership unambiguous, and the middle tokens make the flag's job legible without opening the dashboard.
5. **Require a description and an exit criterion at creation.** Every flag has a one-line description (what does it do) and a one-line exit criterion (what conditions trigger retirement). Block creation when either is missing. Exit criteria for release flags read like "remove when at 100% for 14 days with no rollback." Exit criteria for experiment flags read like "remove when readout is signed and decision is made." Exit criteria for permission flags read like "remove when plan model is consolidated." Exit criteria for operational flags read like "remove when the legacy dependency is decommissioned." Flags without exit criteria are debt by construction.
6. **Make ownership a first-class field.** Every flag is owned by a person at creation and a team at all times. If the person leaves the team, ownership transfers to the team lead within seven days or the flag enters review. Flags whose owner has left the company and whose team has dissolved are the canonical debt-flag pattern; they must surface in a monthly report.
7. **Set lifetime expectations and gates.** Release and experiment flags have a 90-day soft expiry and a 180-day hard expiry by default. Soft expiry triggers an owner notification with a one-click "extend by 30 days, with reason" action. Hard expiry triggers a review by the platform team and an inability to add new traffic to the flag until reviewed. Permission and operational flags are exempt from the expiry mechanism but appear in an annual review. The 90- and 180-day numbers should be tuned to the team's cadence, but the mechanism is not optional.
8. **Build the kill-switch register.** A kill switch is a class of operational flag with two specific properties: it can be flipped by on-call without engineering approval, and flipping it produces a known-good degraded mode rather than an outage. Maintain a register of kill switches per service: name, on-call role, scope (what it protects against), default state, expected impact when flipped, runbook link, and last-tested date. A kill switch that has never been tested is a kill switch the team is hoping works; require quarterly drills.
9. **Distinguish kill switches from circuit breakers.** A circuit breaker is automatic; a kill switch is manual. Automatic shedding under detected fault is a circuit-breaker responsibility, not a flag responsibility. Conflating them produces flags that "should have flipped automatically" and incidents that drag because nobody knew it was supposed to be manual.
10. **Design the default state per type.** Release flags default to off and ramp to on. Experiment flags default to control and ramp to the variant split. Permission flags default to least-privilege (off unless explicitly enabled by an entitlement). Operational flags default to the normal (non-degraded) state. Make the default state a required field at creation; a flag with no default state in code is a bug, not a flag.
11. **Specify how flag state reaches consumers.** Server-side evaluation is the safe default — the client receives the result, not the rule, so the flag platform can change rules without a redeploy. Client-side evaluation (mobile apps with offline support, edge functions with strict latency budgets) is permitted with a cached ruleset and a documented staleness window. Forbid client-side evaluation of permission flags that gate sensitive data; an offline cache that grants access after entitlement revocation is a security defect.
12. **Make rollout shapes explicit.** For release flags, the default rollout is canary at 1% for 24 hours, then 10% for 48 hours, then 50% for 48 hours, then 100%. Each step has a watch: error rate, latency, primary user-facing metric. For experiment flags, the rollout is the assignment function — pre-registered split, no manual nudging. For permission flags, rollout is by rule (plan, account, region); there is no percentage ramp. For operational flags, rollout is binary or graded with explicit thresholds. Document the default rollout shape per type so on-call does not have to invent it on the fly.
13. **Plan for multi-region and edge.** If the platform serves multiple regions or runs on edge infrastructure, define the consistency model. Some flags must be strongly consistent across regions (compliance, geo-restricted features); some can tolerate eventual consistency (UI experiments). State the consistency requirement per flag at creation. Edge-evaluated flags have a maximum staleness in seconds; document it.
14. **Address mobile app store cadence.** Mobile apps update on the user's schedule, not the team's. A flag in a native app can be live in an app version that some users have not upgraded. The policy: every native-app flag has a minimum app version it requires, the platform short-circuits evaluation below that version, and the flag retirement plan accounts for the long tail of un-updated installs (often 12–18 months).
15. **Set a debt threshold and a measurement.** Debt is the count of flags past hard expiry, plus the count of flags with no owner, plus the count of flags with no exit criterion. Publish the number weekly. Set a team-level target (for example, "no more than 2% of flags past hard expiry, no flags without owner"). When the number rises, the platform team has an authoritative trigger to push back; without a number, debt arguments are political.
16. **Run a quarterly retirement sweep.** Once per quarter, every team retires the flags that have met their exit criteria. Retirement is a code change (remove the conditional), a flag-platform change (archive the flag), and an analytics check (confirm no observable behavior change at retirement). Treat retirement as a normal engineering task; budget hours for it explicitly so it does not lose to feature work.
17. **Use a flag-debt rotation.** Some organizations rotate a "flag wrangler" responsibility week by week. The wrangler reviews creations, surfaces stale flags to owners, and runs the retirement sweep. Rotation distributes the work and prevents one team from carrying the policy alone.
18. **Address regulated workloads explicitly.** SOC 2 controls expect documented change management on releases. Flag-gated rollouts count as changes; the platform must produce an audit log of who flipped what when, and the policy must distinguish flag flips that count as changes (release, permission for compliance scope, operational that affects compliance scope) from flips that do not (experiment assignment changes within a pre-approved test). HIPAA, PCI, and similar regimes add their own log retention and access-control requirements. Name the regime per workload.
19. **Plan for the flag-platform outage.** What happens when the flag platform itself is unavailable? Define the failure mode per flag type: release flags fail closed (treat as off) so a degraded platform cannot accidentally launch a feature; experiment flags fail closed (treat all traffic as control) so a degraded platform does not corrupt analysis; permission flags fail closed (deny access) so a degraded platform does not grant elevated privileges; operational kill switches fail open with the last known-good cached state so the platform can still shed load. Code the fallbacks; do not assume the platform is always up.
20. **Make the flag SDK uniform across services.** A single flag SDK per language reduces cognitive load and produces consistent telemetry. The SDK emits exposure events (which flag, which value, which unit) automatically, which is the same telemetry experimentation depends on; the dual purpose justifies the standardization investment. If multiple SDKs exist for historical reasons, define a deprecation path and a date.
21. **Forbid stringly-typed flag keys in production code.** Flag keys live in a generated constants file with type-safe accessors. A misspelled flag key is silently always-off; a typed accessor catches the bug at compile or at test time. Generate the constants from the flag platform's source of truth on every build.
22. **Map flags to incidents in postmortems.** Every incident postmortem includes a "flags involved" section: which flags were on at the time, which were flipped during recovery, which should have existed but did not. The postmortem feeds the kill-switch register and the operational-flag backlog. Over time the register becomes a list of well-tested levers that on-call actually trusts.
23. **Stage the cleanup of existing debt.** When the current state is "we have hundreds of flags and most are stale," the cleanup is not a one-week project. Week 1: inventory and ownership assignment, attaching an owner team to every flag. Week 2: triage by type, putting every flag into one of the four buckets and flagging the mixed-type cases for refactor. Weeks 3–4: retire the obvious — release flags at 100% for months with no rollback signal, experiment flags whose tests ended quarters ago. Weeks 5–8: refactor the type-mixed cases. Weeks 9–12: institute the lifecycle policy and the weekly debt metric. Stage with explicit owner roles and exit criteria for each stage.
24. **Resist policy overreach.** A policy that no team can follow is worse than no policy. Calibrate gates to the team's actual cadence: a four-day-release shop can have 90-day soft expiry on release flags; a quarterly-release shop needs longer. Negotiate the numbers with the engineering leads who will live with them; impose only the non-negotiables (typed accessors, exposure events, ownership, exit criteria, kill-switch register).
25. **Return two artifacts.** The taxonomy and policy document defines the four flag types, the naming convention, the lifecycle policy, the kill-switch register pattern, the failure modes, and the regulated-workload addenda. The cleanup plan is a week-by-week schedule for moving from the current state to the policy state, with owner roles and measurable exit criteria for each phase.

## Inputs

- `current_state` — flag count and categories, platform in use, current pain points.
- `organization_size` — team size, services, deploy cadence, regulated workloads.
- `platform` (optional) — current or planned flag platform.
- `priorities` (optional) — top fix targets.
- `constraints` (optional) — stack, regions, edge, mobile, on-prem.

## Outputs

- A taxonomy and lifecycle policy: four flag types with contracts, naming, ownership, lifetime, default rollout, failure modes, audit logging, and a kill-switch register pattern.
- A staged cleanup plan with weekly milestones, owner roles, exit criteria, and a debt metric that prevents regression.

## Examples

**Example 1: Mid-stage SaaS, accumulated debt.**

*Input* — current: 280 flags across 30 services on Unleash, mostly created in the last 18 months, no consistent naming, owners frequently absent, support team occasionally surprised by a flag flip; org: 70 engineers, weekly release cadence, SOC 2 audit due in 4 months; priorities: audit readiness, kill-switch coverage on the payments service; constraints: TypeScript and Go primary stacks, two regions.

*Plan sketch* — Adopt the four-type taxonomy with `{type}_{surface}_{purpose}_{owner-team}` naming. Implement the typed-accessor SDK pattern across both languages, generated from the platform API. Build the kill-switch register starting with payments: name three kill switches (third-party processor fallback, fraud-rule strict mode, refund-pause), assign on-call rotation, write runbooks, schedule a quarterly drill. Establish the debt metric and publish weekly. Cleanup: week 1 ownership assignment, week 2 type triage, weeks 3–4 retirement of unambiguous release-at-100% cases (estimated 90 of the 280), weeks 5–8 refactor type-mixed cases (estimated 40), weeks 9–12 policy institution. Audit-readiness: ensure platform audit log captures who-flipped-what-when on release and permission flags; configure permission-flag fallbacks to fail closed.

**Example 2: Early-stage startup, before-the-fact policy.**

*Input* — current: 20 flags on GrowthBook, mostly experiments, team feels the policy "before we get to 200 flags"; org: 12 engineers, daily release cadence, no regulated workloads yet; priorities: not slowing the team down; constraints: minimal — small team.

*Plan sketch* — Light policy. The four-type taxonomy is overkill at 20 flags; impose the two distinctions that matter most: separate release flags from experiment flags, and require a one-line description and exit criterion on every flag. Soft expiry at 90 days, hard expiry at 180. No kill-switch register yet; the conversation about kill switches will start with the first production incident. Adopt the typed-accessor SDK pattern now while there is little code to refactor. Skip the rotation; the engineering lead reviews flags monthly. Revisit the policy at 100 flags.

**Example 3: Regulated workload, kill-switch focus.**

*Input* — current: 60 flags on an in-house platform, the team had a near-incident when a permission flag was accidentally flipped on; org: 25 engineers, biweekly release cadence, HIPAA and SOC 2 in scope; priorities: failure-mode discipline, audit logging; constraints: on-prem deploy in some customer accounts.

*Plan sketch* — Permission flags' failure modes are now the top priority. Code permission flags to fail closed (deny) when the flag platform is unreachable. Add a server-side allowlist check independent of the platform for high-sensitivity entitlements; the flag is a convenience, the entitlement decision lives in the entitlement service. Make all flag flips on permission and operational types require a second approver. Implement an immutable audit log with one-year retention. Build the kill-switch register starting with data-access kill switches: a "deny new exports" switch, a "force re-auth" switch, a "drop cache and re-check entitlements" switch. Test each quarterly. Cleanup: smaller scope but with stricter exit criteria. Address the on-prem deploy by versioning the policy alongside the binary so customer accounts know which policy applies.

## Limitations

- The skill produces policy, not platform configuration; concrete YAML or API calls depend on the specific flag platform in use.
- Recommendations on regulated workloads (HIPAA, PCI, SOC 2) are starting points; security and compliance teams must review against the specific control matrix in scope.
- Kill-switch design depends on the architecture being protected; the skill names patterns but cannot enumerate kill switches for an unknown service.
- The skill assumes English-language flag names and documentation; non-English engineering organizations should localize the policy with team-relevant terminology.
- The skill does not select a platform or compare vendors; it describes a policy that should apply across platforms.
- Flag-platform outage planning depends on which features of the platform are in use; the skill names the failure modes but cannot test the SDKs.
- Some recommendations (typed-accessor SDK, exposure-event uniformity) require engineering investment; the skill names them as long-term standards, not as one-quarter projects.

## Sources reviewed

- https://github.com/Unleash/unleash
- https://github.com/growthbook/growthbook
- https://github.com/PostHog/posthog
- https://github.com/open-feature/spec
- https://github.com/featurehub-io/featurehub
- https://github.com/etsy/feature
