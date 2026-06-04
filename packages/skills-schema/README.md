# @skillsgit/skills-schema

Zod schemas and TypeScript types for the `skills.md` frontmatter format.

This package mirrors the canonical Pydantic model that lives in `apps/api`
(see `prompts/shared/skills-md-spec.md` for the spec). Both validators must
accept and reject the same documents; drift is a bug.

Consumed by `apps/web-creator` (compile/validate the visual builder output) and
`apps/web-marketplace` (preview rendering).
