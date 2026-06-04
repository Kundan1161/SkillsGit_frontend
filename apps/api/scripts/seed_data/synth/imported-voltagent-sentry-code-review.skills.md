---
id: skillsgit-curated/imported-voltagent-sentry-code-review
version: 1.0.0
name: Sentry Code Review
description: Perform code reviews following Sentry engineering practices — security, performance, testing, and design review with actionable, empathetic feedback.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, code-review, security, performance]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [code review, pr review, sentry review, n+1 query, sql injection review]
example_invocations:
  - Review my PR against Sentry's code review checklist
  - Look for N+1 queries and security issues in this diff
  - Decide which findings should block this PR
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Sentry Code Review

Follow these guidelines when reviewing code for Sentry projects.

## When to use

Use this skill when reviewing pull requests, examining code changes, or providing feedback on code quality.

## How to apply

Walk the review checklist below. Be polite and empathetic. Provide actionable suggestions, not vague criticism. Phrase as questions when uncertain ("Have you considered…?"). Approve when only minor issues remain — don't block for stylistic preferences.

## Review Checklist

### Identifying Problems

- **Runtime errors** — potential exceptions, null pointers, out-of-bounds access.
- **Performance** — unbounded O(n²), N+1 queries, unnecessary allocations.
- **Side effects** — unintended behavioral changes affecting other components.
- **Backwards compatibility** — breaking API changes without migration path.
- **ORM queries** — complex Django ORM with unexpected query performance.
- **Security** — injection, XSS, access control gaps, secrets exposure.

### Design Assessment

- Do component interactions make logical sense?
- Does the change align with existing architecture?
- Are there conflicts with current requirements or goals?

### Test Coverage

- Functional tests for business logic.
- Integration tests for component interactions.
- End-to-end tests for critical user paths.

Verify tests cover actual requirements and edge cases. Avoid excessive branching or looping in test code.

### Long-Term Impact — Flag for senior review when

- Database schema modifications.
- API contract changes.
- New framework or library adoption.
- Performance-critical code paths.
- Security-sensitive functionality.

## Feedback Tone

- Be polite and empathetic.
- Provide actionable suggestions, not vague criticism.
- Phrase as questions when uncertain.

## Approval

- Approve when only minor issues remain.
- Don't block PRs for stylistic preferences.
- The goal is **risk reduction, not perfect code**.

## Common Patterns to Flag

### Python/Django

```python
# Bad: N+1 query
for user in users:
    print(user.profile.name)

# Good: Prefetch related
users = User.objects.prefetch_related('profile')
```

### TypeScript/React

```typescript
// Bad: Missing dependency in useEffect
useEffect(() => {
  fetchData(userId);
}, []);

// Good: Include all dependencies
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

### Security

```python
# Bad: SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Good: Parameterized
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

## References

- Sentry Code Review Guidelines: https://develop.sentry.dev/engineering-practices/code-review/

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/code-review (Apache-2.0)
