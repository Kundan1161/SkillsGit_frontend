# shared — API Conventions

**Phase:** 0 (foundation)
**Depends on:** `01-tech-stack-and-repo.md`
**Parallel-safe with:** other shared/* prompts
**Status:** ready

> Every new endpoint follows these conventions. If yours can't, justify in a comment in the router and link the prompt that overrode it.

---

## URL structure

- All endpoints under `/v1/...`. New major versions get `/v2/`, never breaking changes in place.
- Plural resource collections: `/v1/skills`, `/v1/orders`, `/v1/reviews`.
- Singular for actions on a resource: `/v1/skills/{id}/publish`, `/v1/orders/{id}/refund`.
- Nested routes only when the child has no independent identity: `/v1/skills/{id}/versions`, `/v1/skills/{id}/reviews` (review still has its own `/v1/reviews/{id}`).

---

## Methods

- `GET` for reads, no side effects.
- `POST` to create or trigger actions.
- `PATCH` for partial updates. Body is a partial of the resource.
- `PUT` only when fully replacing a resource (rare — prefer PATCH).
- `DELETE` for removal. Returns 204 with no body.

---

## Status codes

- `200 OK` — successful read or mutation that returns the resource.
- `201 Created` — successful creation; include `Location` header.
- `202 Accepted` — async work queued; include `Location` to the job-status endpoint.
- `204 No Content` — successful mutation that returns nothing (e.g., DELETE).
- `400 Bad Request` — malformed request body or query.
- `401 Unauthorized` — no/invalid credentials.
- `403 Forbidden` — authenticated but not permitted.
- `404 Not Found` — resource doesn't exist or caller can't see it (don't leak existence).
- `409 Conflict` — state violation (e.g., publishing a draft that's already published).
- `422 Unprocessable Entity` — body parsed but failed business rule validation.
- `429 Too Many Requests` — rate-limited. Include `Retry-After`.
- `500 Internal Server Error` — bug. Include trace id in body.

---

## Error format

Every non-2xx response uses this body shape (Pydantic model `ErrorResponse`):

```json
{
  "error": {
    "code": "skill.publish_validation_failed",
    "message": "Skill failed validation; see details.",
    "details": [
      {
        "field": "frontmatter.ai.required_models",
        "code": "unknown_model_id",
        "message": "Model 'claude-2' is not in the allowlist."
      }
    ],
    "trace_id": "01HX...",
    "doc_url": "https://docs.skillsgit.com/errors/skill.publish_validation_failed"
  }
}
```

- `code` is dotted lowercase, namespaced by module. The frontend uses it for i18n keys and decision logic — never parse the human message.
- `details` is optional, an array of field-level errors. Present for 422.
- `trace_id` is required; pulled from the request's structured-logging context.
- `doc_url` is optional but encouraged for high-cardinality errors.

---

## Pagination

Cursor-based, not offset-based. Every list endpoint accepts and returns the same shape:

**Request query params:**
- `limit` (int, default 20, max 100)
- `cursor` (opaque string, optional)
- `order` (optional, see filtering)

**Response:**
```json
{
  "items": [...],
  "page": {
    "next_cursor": "eyJpZCI6Ii4uLiJ9",
    "has_more": true,
    "limit": 20
  }
}
```

- Cursor is a base64-encoded JSON: `{"id": "<last-id>", "v": "<sort-tiebreaker>"}`. Implement decode/encode in `apps/api/src/core/pagination.py`. Validate signature with HMAC of platform key so cursors can't be forged.
- If a client passes `cursor` with mismatched filters, return 400 — don't silently re-paginate.

---

## Filtering & sorting

- Filters are query params named after the field: `?category=finance&pricing_model=one_time`.
- Multi-value filters: comma-separated (`?tags=dcf,valuation`) — OR semantics within a field, AND across fields.
- Sorting: `?order=-rating_avg,name` (minus prefix = descending). Allowed sort fields are explicitly enumerated per endpoint; reject unknown fields with 400.
- Free-text search: `?q=...`. Postgres tsquery with `websearch_to_tsquery`. Defer typo tolerance to Phase 2.

---

## Idempotency

- All `POST` endpoints that take money or mutate billing accept an `Idempotency-Key` header (uuid). Store `(user_id, key) -> response` in Redis for 24h. Re-invocations with the same key + same body return the cached response; same key + different body returns 409.
- The frontend `api-client` injects an idempotency key on every checkout/publish call by default.

---

## OpenAPI

- FastAPI auto-generates OpenAPI; we serve it at `/v1/openapi.json`.
- All routers must set `tags`, `summary`, `response_model`, and an explicit `responses` map for non-2xx codes that the endpoint emits.
- `packages/api-client` regenerates TS types on `pnpm codegen`. CI fails if the generated client differs from committed.
- All Pydantic models in API surfaces have `model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [...]})` so OpenAPI examples are populated.

---

## Versioning policy

- Breaking changes: new `/v2`. Old version supported ≥ 6 months after `/v2` launches.
- Non-breaking: adding optional fields, new endpoints, new error codes. Allowed any time.
- Deprecation: respond with `Deprecation: true` and `Sunset: <RFC 9745 date>` headers for a full sprint before removal.

---

## CORS

- Marketplace frontend (Vercel) and creator frontend (Vercel) origins are allow-listed.
- API token requests are not subject to CORS restrictions (server-to-server).
- All cookie-bearing requests must include `credentials: 'include'` from the frontend — `api-client` does this by default.

---

## Background work

- Long-running operations (sandbox runs, import parsing, batched payouts) return 202 with a job id.
- Job status endpoint: `GET /v1/jobs/{id}` returns `{status: "queued"|"running"|"succeeded"|"failed", progress?: 0..1, result?: ..., error?: ...}`.
- Frontend polls every 2s while `status in {queued, running}`, exponential backoff after 30s of waiting.

---

## Webhooks (outbound to creators)

Creators can register webhook URLs for events on their skills (`skill.purchased`, `subscription.created`, `subscription.canceled`, `review.created`, `version.published`).

- Each event signed with HMAC-SHA256 over the JSON body, header `X-Skillsgit-Signature: v1=<hex>`.
- Retry policy: at-least-once, exponential backoff up to 24h, give up after 24h with a failure email.
- See `marketplace/07-creator-dashboard.md` for the UI to manage webhooks.

---

## Acceptance

- [ ] `ErrorResponse` model exists in `apps/api/src/core/errors.py` with a global exception handler that maps all `HTTPException` and `RequestValidationError` to it.
- [ ] Pagination helper exists in `apps/api/src/core/pagination.py` with cursor encode/decode + HMAC.
- [ ] Idempotency middleware exists, gated on `Idempotency-Key` header.
- [ ] At least one endpoint per module demonstrates each convention; documented as canonical reference in `docs/api-style.md`.
- [ ] `pnpm codegen` produces a typed TS client; CI enforces it's committed.
