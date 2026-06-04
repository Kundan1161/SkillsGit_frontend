---
id: skillsgit-curated/imported-voltagent-sentry-security-review
version: 1.0.0
name: Sentry Security Review
description: Identify exploitable security vulnerabilities with high confidence, following OWASP standards — trace data flow, verify attacker control, and report only confirmed findings.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, security, owasp, vulnerability]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [security review, owasp, vulnerability assessment, exploit confirm]
example_invocations:
  - Security review this Django view for injection
  - Audit the auth flow for high-confidence vulnerabilities
  - Check this diff against OWASP top 10
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Sentry Security Review

## When to use

Use this skill when conducting security code reviews — identifying exploitable vulnerabilities with high confidence and following OWASP standards.

## How to apply

**Research before reporting.** Trace data flow from sources to sinks, verify attacker control, and confirm exploitability before flagging an issue. Distinguish server-controlled values (settings, env vars, hardcoded constants) from user input. Use framework context — Django auto-escape, ORM parameterization, etc. — to discount theoretically dangerous patterns that are mitigated in practice.

## Principles

1. **Research before reporting** — Trace data flow, check configurations, verify attacker control.
2. **High confidence only** — Report vulnerabilities confirmed exploitable, not theoretical patterns.
3. **Distinguish sources** — Server-controlled values are safe; user input is investigated.
4. **Framework context matters** — Check for built-in mitigations.
5. **Scope discipline** — Review what you're given; research the codebase to build confidence.

## Workflow

When asked to security review code:

- Load relevant OWASP references and language/infrastructure guides.
- Trace input sources and validate exploitability.
- Report only HIGH-confidence findings with severity levels.
- Note MEDIUM-confidence items for further verification.
- Skip theoretical issues, test code, and framework-mitigated patterns.

## Output

For each HIGH finding:

- File:Line
- Severity
- Source → Sink trace
- Concrete payload that would exploit it
- Recommended fix
- Reference (OWASP / CWE)

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/security-review (Apache-2.0)
