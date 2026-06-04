---
id: skillsgit-curated/salesforce-security-review
version: 1.0.0
name: Salesforce Security Review
description: Review a Salesforce org for security posture - profiles vs permission sets, sharing model, FLS, integrations, OAuth scopes, and Shield-eligible controls.
authors:
  - name: Wave-3 Synthesis Agent
    handle: synth-wave3
    role: author
category: enterprise-software
tags:
  - niche:salesforce-development
  - security
  - permissions
  - sharing
  - named-credentials
  - oauth
  - shield
license_type: free
ai:
  required_models:
    - claude-opus-4-7
    - claude-sonnet-4-6
  compatible_models:
    - claude-haiku-4-5
    - gpt-4o
  min_context_tokens: 24000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - salesforce security review
  - permission set vs profile
  - sharing model audit
  - field-level security
  - named credential
  - oauth scope salesforce
  - shield encryption
  - org security posture
  - appexchange security review
  - sf code analyzer security
example_invocations:
  - Audit our org's permission model — we still rely on profiles.
  - Review our integrations — are we still using usernames and passwords anywhere?
  - Help me prepare for an AppExchange security review.
  - Is our sharing model correct for a multi-region sales team?
inputs:
  - name: scope
    type: choice
    required: true
    description: What is being reviewed.
    choices: [whole-org, integration-layer, managed-package-for-appexchange, single-object-model]
  - name: artefacts
    type: text
    required: false
    description: Profile / perm-set names, integration endpoints, sharing rules, or other artefacts available for inspection.
  - name: risk_appetite
    type: choice
    required: false
    description: Drives severity calibration.
    choices: [enterprise-conservative, mid-market-balanced, startup-moving-fast]
outputs:
  - name: findings
    type: markdown
    description: Severity-ranked findings with concrete remediation.
  - name: hardening_plan
    type: markdown
    description: Phased remediation plan (immediate / 30-day / 90-day).
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Salesforce Security Review

## When to use

Use this skill when reviewing a Salesforce org or managed package for security
posture across one or more of:

- Permission model (profiles, permission sets, permission set groups, muting
  permission sets).
- Sharing model (OWD, role hierarchy, sharing rules, manual sharing, restriction
  rules, Apex managed sharing).
- Field-level security (FLS) and object-level CRUD.
- Integration security (Named Credentials, External Credentials, OAuth flows,
  scopes, certificate management).
- Apex / LWC security boundaries (sharing keywords, USER_MODE, CSP, locker
  service, third-party scripts).
- Platform encryption / Shield (probabilistic vs deterministic, key management,
  monitoring).

Trigger on phrases like "security review", "permission audit", "we're using
profiles everywhere", "are we ready for AppExchange security review", "is this
integration safe", "field-level security check".

Do **not** use this skill for:

- Customer-facing portal security (Experience Cloud / Communities) past the
  permission-model basics; that has its own threat model (guest user, link
  unfurling, public records) deserving a dedicated review.
- Identity provider configuration (SSO, MFA enforcement, session management) —
  in scope at the policy level only.

## How to apply

### Step 1 — Frame the review

Restate scope and the threat actors the review prioritises. The Salesforce
threat model has four canonical actors:

1. **Authenticated internal user** with elevated curiosity — biggest cause of
   data leak incidents; rotation and segregation of duties matter.
2. **Authenticated partner / community user** — has narrower data access by
   design but is most often misconfigured (guest user, public records).
3. **External attacker via integration** — exploits over-scoped OAuth tokens
   or hard-coded credentials.
4. **Departed employee with retained access** — deactivation hygiene and
   token revocation.

Calibrate severity against `risk_appetite`:

- `enterprise-conservative`: every "Modify All Data" assignment outside Sys
  Admin is a BLOCKER; ageing OAuth tokens are MAJOR.
- `mid-market-balanced`: BLOCKER for unrestricted Modify All Data on standard
  business profiles; MAJOR for ageing tokens.
- `startup-moving-fast`: BLOCKER for credential exposure, integration auth
  failures, public guest-user data; everything else MAJOR or lower.

### Step 2 — Permission model

**Anti-pattern: customisations on profiles.** Salesforce's official direction
since Spring '23 has been "user access via permission sets and permission set
groups; profiles minimal". Each finding below is severity MAJOR unless noted.

Checks:

1. Enumerate every non-standard profile. For each, list permissions delta
   from the corresponding standard profile. Any profile with > 5 custom
   object permissions or > 10 custom field permissions: recommend migrating
   those permissions to a named permission set.
2. **Profiles with "Modify All Data" or "View All Data".** Only System
   Administrator should hold these. Any other profile: BLOCKER under
   enterprise-conservative, MAJOR otherwise.
3. **Profiles with "Author Apex".** Only developer profiles should have it.
   Production end-users with this permission can introduce bypasses.
4. **Permission Set Groups** should be the default vehicle for role-based
   access. Flat permission set sprawl (a user assigned 12 individual permission
   sets) is a maintainability MAJOR finding; recommend collapsing into PSGs.
5. **Muting Permission Sets** are appropriate for "this group should have the
   sales bundle EXCEPT the export-data permission". Verify any muting set is
   documented (without documentation, a future admin will undo it).
6. **API-only profiles for integration users.** Integration system accounts
   should have a dedicated profile with `API Enabled = true` and only the
   object/field perms strictly required. No UI, no Modify All, no Author Apex.
7. **Login IP ranges and login hours.** Profiles serving integration users
   should be IP-restricted to known callout origins. Missing IP restriction
   on integration profile: MAJOR.
8. **Session settings.** "High Assurance" required for sensitive ops; session
   timeout ≤ 2 h for internal users; force logout on session timeout.

### Step 3 — Sharing model

For each custom object and each customisable standard object in scope:

1. **OWD.** What is the Organization-Wide Default for internal and external
   users? Defaults of "Public Read/Write" on a customer-data object are MAJOR
   under any risk appetite. "Public Read Only" is acceptable for reference
   data but should be deliberate.
2. **Role hierarchy.** Verify it reflects reporting / access actually intended.
   Mis-rooted users (e.g. an integration user reporting to the CEO node) leak
   data upward unintentionally.
3. **Sharing rules.** Count criteria-based rules per object. > 25 on one
   object is a performance MAJOR (sharing recalculation cost). Recommend
   restructuring with ownership-based rules, role-based access, or restriction
   rules.
4. **Restriction rules.** Salesforce's newer "deny by default" tool. Verify
   any object with public sharing actually relies on restriction rules to
   narrow access; absence of restriction rules on a sensitive object with
   broad OWD: MAJOR.
5. **Apex managed sharing.** Any `Share` object insertion in Apex must use
   `RowCause` that is custom-defined (declared on the parent), not
   `RowCause.Manual`. Manual cause from Apex is a MAJOR.
6. **Public groups / queues.** Enumerate; check membership; any group with
   "All Internal Users" as a member and Modify access on sensitive data:
   BLOCKER.
7. **Guest user.** Any community / experience site's guest user profile
   should have **zero** record access by default. If `Read` is granted on
   any object: review the public-facing pages and verify FLS prevents data
   leak. Recent Salesforce CVEs have centred on this.

### Step 4 — Field-level security

1. Sample 10 high-sensitivity fields (PII, financial, regulated). For each,
   verify:
   - FLS is denied on every profile / perm-set EXCEPT those that legitimately
     need it.
   - The field is referenced in Apex with USER_MODE / `WITH USER_MODE` (see
     step 7) so the runtime honours FLS automatically.
   - The field is not exposed in a public-context page (community guest, force.com
     site, public report).
2. **Field history tracking.** Sensitive fields should be tracked; absence on
   PII fields is a MINOR (regulatory readiness).
3. **Encrypted text fields.** "Classic encrypted" custom fields are deprecated
   for new use; recommend Shield Platform Encryption instead.

### Step 5 — Integration security

Run this checklist per integration:

1. **Auth mechanism.** Must be OAuth 2.0 via a Connected App (JWT bearer or
   authorization code with PKCE). Username/password OAuth flow is BLOCKER.
   Hard-coded password in Apex is BLOCKER.
2. **Named Credentials.** Endpoint URL + auth bundle must live in a Named
   Credential, not in Apex strings. Apex calls the endpoint via
   `callout:MyNamedCredential/...`. Hard-coded `https://...` URLs in Apex:
   BLOCKER.
3. **External Credentials + Permission Set Mapping.** The newer (Winter '23+)
   model separates the endpoint (Named Credential) from the auth (External
   Credential), and authorisation is granted to specific permission sets.
   Verify permission sets are minimal — no "All Users" mapping.
4. **OAuth scopes on Connected Apps.** Apply the principle of least privilege:
   `api`, `refresh_token`, `offline_access` are typical; `full` is rarely
   appropriate. `web` (start OAuth dance from web) only if your integration
   needs interactive login. Each scope grants a real capability; over-scoping
   is MAJOR.
5. **Refresh token policy.** Connected App should set "Immediately expire
   refresh token" if integration is short-lived; "Refresh token is valid
   until revoked" only with monitoring on token age. Tokens older than 6 months
   on critical integrations: MAJOR.
6. **IP relaxation.** Connected App should "Enforce IP restrictions" so the
   integration profile's IP range applies even with refresh tokens.
7. **Certificate hygiene.** If using mutual TLS / JWT bearer, the certificate
   under `Certificate and Key Management` must be ≤ 12 months from creation,
   and the corresponding consumer key rotated when the cert is rotated.
   Stale certificates: MAJOR.
8. **Inbound integration.** Any `@RestResource` / `@HttpGet` / `@HttpPost`
   Apex class is an inbound surface. Verify:
   - `with sharing` keyword on the class.
   - Input validation (`String.isBlank`, allow-list, type coercion).
   - Output sanitisation (no leakage of internal Ids beyond what the caller
     should see).
   - Rate limiting via Connected App's "Permitted Users" + IP relaxation.

Reference: `forcedotcom/code-analyzer` (BSD-3-Clause) ships rule
`ApexBadCrypto`, `ApexCRUDViolation`, `ApexSOQLInjection`, `ApexOpenRedirect`,
`ApexSharingViolations`, and `ApexUnescapedHtmlParam` — name findings using
these canonical ids so developers can cross-reference scanner output.

### Step 6 — Apex / LWC code-level security

For Apex:

- Every `@AuraEnabled` class declares `with sharing`. Missing: BLOCKER.
- `WITH USER_MODE` on SOQL or `Database.AccessLevel.USER_MODE` on DML for any
  user-context operation. Migrating from `WITH SECURITY_ENFORCED` is
  recommended (USER_MODE filters rather than throws). Lack of either: MAJOR.
- Dynamic SOQL uses bind variables or `String.escapeSingleQuotes`. Absence:
  BLOCKER (SOQL injection).
- `@AuraEnabled(cacheable=true)` methods read-only by design; verify.
- Custom exception types thrown to the client must not leak internal stack
  traces or query strings.

For LWC:

- `lwc:dom="manual"` usage carefully reviewed (allows raw DOM, breaks
  Locker/LWS guarantees).
- `lightning/uiRecordApi` preferred for record CRUD over imperative Apex; it
  enforces FLS/CRUD automatically.
- Third-party JavaScript imports via `lightning/platformResourceLoader` only,
  and the static resource is hosted in-org (not loaded from a CDN). External
  CDN loads in LWC: BLOCKER on Lightning Locker, MAJOR on LWS.
- CSP trusted sites configured for any non-Salesforce origin the LWC contacts.

For Visualforce (legacy):

- Pages that render user input use `{!HTMLENCODE(...)}` or `{!JSENCODE(...)}`.
- `apex:includeScript` from non-static-resource URL: MAJOR.

### Step 7 — Encryption and Shield

If Shield is licensed:

- **Encrypted fields** should cover PII, financial account numbers, and any
  regulated data class (HIPAA PHI fields, GDPR special categories).
- Choose deterministic encryption for fields that need exact-match filtering
  (e.g., SSN lookups), accepting the weaker entropy. Probabilistic for the
  rest.
- **Tenant Secret rotation** on schedule (annual minimum); verify Last Active
  Date in setup.
- **Event Monitoring** enabled for at least: Login, API, Apex Execution,
  Report Export, URI. Event Monitoring streams should land in a SIEM, not be
  reviewed manually.
- **Field Audit Trail** retention configured for sensitive fields (default
  18 months on standard, up to 10 years with Shield).

If Shield is not licensed, recommend the **minimum** native controls:

- Classic Encrypted Custom Fields for the most sensitive ~5 fields (knowing
  the deprecation direction).
- Setup Audit Trail download monthly to a long-term store.

### Step 8 — Render findings and hardening plan

Output two artefacts:

1. **Findings** — a table with: ID, severity, category, location, message,
   remediation pointer. Group by category (permission model, sharing, FLS,
   integration, code, encryption).
2. **Hardening plan** — phased:
   - **Immediate (this week):** all BLOCKERs.
   - **30 days:** MAJORs that require code or config change but no migration.
   - **90 days:** MAJORs that require migration (profile-to-perm-set,
     `WITH SECURITY_ENFORCED` → USER_MODE, classic encryption → Shield),
     plus any MINORs the team chooses to pull forward.

For AppExchange security review preparation specifically, add a section
mapping findings to the Salesforce ISV Security Review checklist categories:
"Storing data securely", "Sharing data securely", "Communicating data
securely", "Authentication", "Insecure functions", "Open redirects",
"Cross-site scripting". Reviewers expect this mapping.

## Inputs

- `scope` (required) — drives which sections are deep-dived.
- `artefacts` (optional but recommended) — without artefacts the review is
  generic; with profile names / integration list / sharing rules it becomes
  specific and actionable.
- `risk_appetite` (optional) — severity calibration.

## Outputs

- `findings` (markdown) — categorised findings table.
- `hardening_plan` (markdown) — phased remediation plan.

## Examples

### Example 1 — Mid-market org, integration-layer scope

Inputs: scope=integration-layer, artefacts=list of 6 integrations (Stripe,
NetSuite, Mailchimp, Snowflake, ZoomInfo, an internal data-platform).
Risk appetite=mid-market-balanced.

Expected findings: 2 BLOCKER (Mailchimp using username/password flow,
internal platform using hard-coded endpoint), 4 MAJOR (Stripe Connected App
has `full` scope, NetSuite refresh token 14 months old, ZoomInfo Named
Credential exists but Apex bypasses it once, Snowflake integration profile
lacks IP restriction), 2 MINOR. Hardening plan: this week migrate Mailchimp
to OAuth + Named Credential, externalise the internal endpoint; 30 days
scope-tighten Stripe, rotate NetSuite token; 90 days adopt External
Credentials + perm-set mapping across all six.

### Example 2 — Managed-package-for-appexchange scope

Inputs: scope=managed-package-for-appexchange.

Expected findings: ordered by Salesforce ISV Security Review categories.
Common issues: missing `with sharing`, dynamic SOQL without escaping,
unenforced FLS in `@AuraEnabled` methods, unsanitised input in inbound REST
endpoints, scripts loaded from external CDN, ungrouped permission sets.

## Limitations

- **No live org access.** This skill reasons from artefacts the user supplies.
  Recommend the user run `sf code-analyzer run --rule-selector security` and
  paste results, and export profiles / permission sets via Metadata API for
  inspection.
- **Compliance frameworks beyond the platform** (SOC 2 controls, HIPAA BAAs,
  GDPR data-subject-rights tooling) are policy questions the skill notes but
  does not fully resolve.
- **Shield licensing.** Several recommendations are only available with
  Shield; alternative non-Shield controls are noted where relevant.
- **Source-thinness disclosure.** Authoritative Salesforce security guidance
  lives almost entirely in Salesforce-owned non-permissive sources
  (Trailhead, Help & Training, Architect Decision Guides, the ISV Security
  Review checklist itself). Permissively-licensed reference material is
  limited to: `forcedotcom/code-analyzer` (BSD-3-Clause), security rule
  catalogues inside `apex-enterprise-patterns/fflib-apex-common` (BSD-3-Clause),
  scanner-output handling in `jongpie/NebulaLogger` (MIT) for audit trails,
  and example secure-deploy steps in `github/octoforce-actions` (MIT) and
  `SFDO-Tooling/CumulusCI` (BSD-3-Clause). The guidance above is the
  synthesist's own restatement of common security practice, cross-checked
  against those permissively-licensed sources where they cover the topic.
