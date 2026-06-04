---
id: skillsgit-curated/imported-voltagent-sentry-django-perf-review
version: 1.0.0
name: Sentry Django Performance Review
description: Review Django code for performance issues — N+1 queries, unbounded querysets, missing indexes, and write loops — with severity-based prioritization and false-positive discipline.
authors:
  - name: Sentry
    handle: getsentry
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, sentry, django, performance, n-plus-one, indexes]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [django performance, n+1 queries, prefetch, bulk_create, missing index]
example_invocations:
  - Review this Django view for performance issues
  - Find N+1 queries in my changes
  - Audit unbounded querysets in list endpoints
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Django Performance Review

## When to use

Use this skill when reviewing Django code for performance issues — especially in hot user-facing paths and list endpoints.

## How to apply

Research first — trace data flow, check for existing optimizations, verify data volume. **Zero findings is acceptable** — don't manufacture issues to appear thorough. Validate every finding before reporting it.

## Priority by Impact

### CRITICAL

1. **N+1 Queries** — Each adds O(n) database trips; 100 rows = 100 extra queries.
2. **Unbounded Querysets** — Memory exhaustion risk; always paginate list endpoints.

### HIGH

3. **Missing Indexes** — Full table scans on large tables (10k+ rows).
4. **Write Loops** — Use `bulk_create()` and `bulk_update()` instead of iterative `save()`.

### LOW

5. **Inefficient Patterns** — Minor style concerns; usually skip unless already reporting real issues.

## Skip / Don't Report

- Test files.
- Admin views.
- Management commands.
- Tables with < 1,000 rows.
- Cold paths.
- Micro-optimizations without evidence of impact.

## Validation Checkpoints

Before reporting any issue, confirm:

- Data flow traced from creation to consumption.
- Existing optimizations searched for.
- Actual data volume verified.
- Code runs on hot paths (user-facing, frequent execution).
- Actual performance impact, not style preferences.

## False Positives (Don't Report)

- Queryset variable assignment (it's lazy).
- Single queries.
- Combining lines into expressions.

## Examples

```python
# CRITICAL: N+1
for user in users:
    print(user.profile.name)

# Fix: prefetch_related
users = User.objects.prefetch_related('profile')

# CRITICAL: Unbounded queryset
def list_users(request):
    return JsonResponse({"users": list(User.objects.all().values())})

# Fix: paginate
def list_users(request):
    page = Paginator(User.objects.all(), 50).get_page(request.GET.get("page"))

# HIGH: Write loop
for item in payloads:
    Item.objects.create(**item)

# Fix: bulk_create
Item.objects.bulk_create([Item(**p) for p in payloads])
```

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `getsentry/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/getsentry/skills/tree/main/skills/django-perf-review (Apache-2.0)
