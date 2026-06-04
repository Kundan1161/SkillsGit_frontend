# API Style

> **Canonical source:** [`prompts/shared/api-conventions.md`](../prompts/shared/api-conventions.md).
> This file is a human-friendly pointer; if anything below conflicts with the canonical spec, the spec wins.

## TL;DR

The Skills Marketplace API is a versioned (`/v1`) JSON-over-HTTPS service emitted by FastAPI. Errors use a uniform problem-details-style envelope, list endpoints are cursor-paginated, all IDs are UUID v7, all money is integer cents, and all timestamps are UTC ISO-8601 with a trailing `Z`. The OpenAPI document at `/v1/openapi.json` is the single source of truth for request/response shapes — frontends consume it through the generated `@skillsgit/api-client` package and never hand-write types.

For full conventions (auth, idempotency keys, rate limits, error codes, pagination cursors), read the canonical spec.
