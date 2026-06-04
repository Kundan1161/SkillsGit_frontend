---
id: jane-devops-demo/2025-01-secret-rotation-zero-downtime
version: 1.0.0
name: 2025-01 Zero-downtime database password rotation across 14 services
description: "[sample data] Rotated a shared Postgres app-role password across 14 services without dropping a single request; the trick was a two-credential overlap window and a per-service health gate."
authors:
  - name: Jane Devops (sample)
    handle: jane-devops-demo
    role: author
category: personas
tags:
  - sample-data
  - secrets
  - rotation
  - postgres
  - security
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models:
    - claude-opus-4-7
trigger_keywords:
  - password rotation
  - secret rotation
  - zero downtime
  - postgres credentials
example_invocations:
  - "How do I rotate a shared database password across many services without a maintenance window?"
kind: memory_neuron
parent_occupation_id: skillsgit-curated/ai-devops-engineer
links:
  - target: base/secrets-architecture-designer
    relation: applies
  - target: base/workload-identity-architect
    relation: see-also
  - target: base/artifact-signing-and-verification-designer
    relation: see-also
neuron:
  situation: |
    Quarterly security review required us to rotate the shared
    application-role Postgres password used by 14 services across 3
    Kubernetes clusters. Previous rotations had taken a 30-minute
    maintenance window and triggered ~6 minutes of 5xx during the
    cutover. Security wanted the window gone; product wanted zero
    error-budget burn.
  decision: |
    Created a second app-role with the new credential and granted it
    the same privileges. Pushed the new secret to all 14 services as
    `DB_PASSWORD_NEXT` (in addition to the existing `DB_PASSWORD`).
    Modified the connection pool to prefer NEXT when present and fall
    back to current on auth failure. Rolled services one at a time
    behind a per-service post-rollout health gate. Once all services
    reported healthy on NEXT for 24 hours, swapped NEXT -> primary and
    revoked the old role.
  outcome: |
    Zero requests dropped during the rotation. Total elapsed: 31 hours
    (14 services * ~1h cooldown + 24h soak). Error-budget burn for the
    week: 0.02% (baseline noise). The two-credential pattern is now in
    our standard rotation runbook and applies to API keys and
    workload-identity tokens too.
  recorded_at: "2025-01-09"
  confidence: 0.9
---

# 2025-01 Zero-downtime database password rotation across 14 services

> SAMPLE DATA — this neuron is part of the seeded `@jane-devops-demo`
> persona shipped alongside the Cycle-1 demo. Real persona neurons are
> published by named DevOps practitioners and replace this content.

## When to use
Apply this when rotating any shared credential (DB password, API key,
service-account token) across more than ~3 services where the cost
of dropped requests is non-zero. The pattern generalizes to any
auth scheme that supports two simultaneous valid credentials; check
this before adopting (Postgres roles, AWS IAM access keys, OIDC
client-secret rotation, OAuth refresh tokens all support it; some
legacy schemes don't).

## How to apply
1. Confirm the auth scheme supports two valid credentials
   simultaneously. If not, this pattern doesn't apply — plan a
   maintenance window instead.
2. Provision the second credential (parallel role / IAM key /
   client secret). Grant identical privileges. Verify both work
   in a staging service.
3. Push the new credential to every service's secret as a NEXT
   field while keeping the current. Patch the shared client
   library to prefer NEXT and fall back to current on auth
   failure.
4. Roll services one at a time, gated on a concrete per-service
   health signal (connection application_name, log tag, etc.),
   not a wall-clock timer.
5. Soak for 24 hours minimum. Include all batch jobs, scheduled
   tasks, and long-lived analytics processes in the soak
   checklist. Use the soak to find connections you forgot about.
6. Promote NEXT to primary, revoke the old credential, remove the
   old secret.

## What happened
Quarterly security required a rotation of the shared `app_writer`
Postgres role's password used by all 14 services in the orders
domain. The role has SELECT/INSERT/UPDATE/DELETE on the orders
schema. Three Kubernetes clusters, multiple replicas per service.

Previous rotations had used a flag-day approach: push the new
password to every service's secret simultaneously, then kill all
pods and watch them come back with the new credential. Two problems:
during the ~6-minute rolling restart window the still-old pods got
auth failures from Postgres (the password had already been changed
server-side), and we burned a 30-minute maintenance window that
involved overnight coordination across three squads.

This time we did it credential-overlap style:

1. Created `app_writer_v2` Postgres role with the new password. Same
   schema privileges. Now both `app_writer` and `app_writer_v2`
   work simultaneously.
2. Updated the secret manager: kept `DB_PASSWORD` (old, still working)
   and added `DB_PASSWORD_NEXT` (new, also working). Both pushed to
   all 14 services' secrets in one batch.
3. Patched the shared db-client library to prefer `DB_PASSWORD_NEXT`
   when set and fall back to `DB_PASSWORD` on auth failure. Shipped
   as a library bump that each service consumed in its normal
   deploy cycle.
4. Rolled each service one at a time. Health gate per service:
   wait until `pg_stat_activity` for the service's pods showed all
   active connections using `application_name=<svc>-v2` (we tagged
   the next-cred connections with a different application_name).
   ~1 hour cooldown between services.
5. After all 14 services were on `DB_PASSWORD_NEXT`, let it soak
   24 hours. Watched for delayed connection-pool refreshes,
   long-lived analytics-job processes, anything that might still be
   using the old credential.
6. End of soak: rotated the secret labels (NEXT -> primary), pushed
   the rename, dropped `app_writer` from Postgres, removed
   `DB_PASSWORD` from secrets.

Total elapsed: 31 hours across the 14-service roll plus the 24h
soak. Zero dropped requests. Error-budget burn for the week was
0.02%, indistinguishable from baseline.

Two things that almost broke the plan:
- The analytics jobs we'd forgotten about. A nightly batch job ran
  at hour 12 of the soak still on `DB_PASSWORD`. The soak window
  caught it; if we'd skipped the soak we'd have killed it at
  rotation time. Added "all batch jobs touched the rotation
  successfully" as an explicit soak checklist item.
- One service had a connection pool with `max_lifetime=24h`. Connections
  established before the patch never refreshed. We hit them with a
  pool-recycle call at hour 8 to force refresh.

## Lessons
- The two-credential overlap window is the right primitive for any
  shared-credential rotation. The window costs ~1 day; the
  alternative (flag-day cutover) costs error budget AND requires
  cross-team coordination on overnight maintenance.
- A per-service health gate beats a global timer. We could have
  said "wait 5 minutes between services" but that's both slower and
  riskier than waiting on a concrete signal (connections by
  application_name).
- The soak window catches the things you forgot about. Always
  include batch jobs, scheduled tasks, long-running analytics
  notebooks, and any cron-like workload in the soak checklist.
- Tag your connections. `application_name` (or equivalent in your
  driver) is free and turns "is this rolled out" from a guess into
  a query.
