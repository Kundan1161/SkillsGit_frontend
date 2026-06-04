---
id: skillsgit-curated/imported-voltagent-firebase-security-rules-auditor
version: 1.0.0
name: Firebase Security Rules Auditor
description: Red-team audit of Firestore security rules — actively seek bypasses, validate authority sources, enforce types, and score from Critical to Secure.
authors:
  - name: Firebase
    handle: firebase
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, firebase, security, firestore-rules, red-team, audit]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [firestore rules audit, security rules red team, firebase rules review, bypass detection]
example_invocations:
  - Audit my Firestore security rules for bypasses
  - Find privilege escalation paths in my rules
  - Score these rules and recommend fixes
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Firebase Security Rules Auditor — Red Team Edition

## When to use

Use this skill when auditing Firestore security rules — actively seek vulnerabilities rather than assuming complexity equals security.

## How to apply

Treat rules as a potential attacker would. Don't trust comments — read the predicates literally. Score each rule set on the five-point severity scale and emit JSON with findings.

## Mandatory Audit Areas

1. **Update Bypass Vulnerability** — Can users create a valid document, then update it into a malicious state?
2. **Authority Source Validation** — Do sensitive fields rely on user-controlled data for permissions (e.g., a `role` field the user can write)?
3. **Business Logic Alignment** — Do rules support actual application functionality, or are they too permissive or too strict?
4. **Resource Exhaustion** — Missing length/size constraints on strings, arrays, or maps.
5. **Type Enforcement** — Are field types validated?
6. **Ownership Verification** — Field-level restrictions versus identity-based access control. (Don't confuse "this field is required" with "only the owner can write".)

## Scoring Scale

- **1 — Critical** — Unauthorized access, privilege escalation, or bypass.
- **2 — Major** — Broken logic, role self-assignment.
- **3 — Moderate** — PII exposure, inconsistent validation.
- **4 — Minor** — Self-data corruption, missing minor checks.
- **5 — Secure** — Comprehensive validation with strict ownership controls.

## Output Format

Return JSON:

```json
{
  "score": 2,
  "summary": "Several major vulnerabilities found.",
  "findings": [
    {
      "severity": 1,
      "rule": "match /users/{uid}",
      "issue": "User can self-assign admin role on update.",
      "remediation": "Add request.resource.data.role == resource.data.role to update rule."
    }
  ]
}
```

## Audit Workflow

1. Enumerate every `match` block and identify the data shape it gates.
2. For each `allow` action, list the conditions and verify each gates an attacker-meaningful field.
3. Check `create` vs `update` paths separately — update bypasses are common.
4. Trace `request.auth` and `request.resource.data` through helper functions.
5. Score and emit findings.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `firebase/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/firebase/skills/tree/main/skills/firebase-security-rules-auditor (Apache-2.0)
