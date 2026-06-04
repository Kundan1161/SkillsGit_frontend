# shared — Authentication & Sessions

**Phase:** 0 (foundation)
**Depends on:** `01-tech-stack-and-repo.md`, `02-data-model-core.md`
**Parallel-safe with:** other shared/* prompts
**Status:** ready

---

## Scope

User accounts, sign-in, sessions, roles, and API tokens. Email verification and password reset are in scope; SSO and SAML are not.

---

## Auth strategy

- **Library:** `fastapi-users[sqlalchemy]` v14+ with JWT strategy.
- **Web sessions:** httpOnly + Secure + SameSite=Lax cookie holding the JWT. Path=`/`, refresh on rolling window.
- **API tokens:** opaque random tokens (32-byte URL-safe, prefixed `skg_live_` or `skg_test_`), stored hashed (argon2id). Issued from the creator dashboard for programmatic skill downloads / publish API.
- **OAuth (Phase 1):** Google and GitHub via `fastapi-users`' OAuth extension. Buyers and creators both can use either.
- **Password storage:** argon2id with default tuning bumped for production (mem=64MB, iterations=3, parallelism=4).

---

## Endpoints

All under `/v1/auth/`:

```
POST /v1/auth/register             { email, password, display_name }
POST /v1/auth/login                { email, password }      → sets cookie
POST /v1/auth/logout                                          → clears cookie
POST /v1/auth/forgot                { email }
POST /v1/auth/reset                 { token, new_password }
GET  /v1/auth/verify?token=...      → marks email verified
POST /v1/auth/verify/resend         { email }
GET  /v1/auth/oauth/{provider}/start
GET  /v1/auth/oauth/{provider}/callback
GET  /v1/auth/me                                              → current user
PATCH /v1/auth/me                   { display_name?, avatar_url? }
```

Creator-specific:
```
POST /v1/auth/become-creator        { handle, payout_country }   → creates creator_profile + starts Stripe Connect onboarding
GET  /v1/auth/tokens                                              → list issued API tokens
POST /v1/auth/tokens                { name, scopes }              → issue new (returns plaintext once)
DELETE /v1/auth/tokens/{id}                                       → revoke
```

---

## Roles & authorization

- `role` on the user is the **primary** role and drives UX defaults (which app/dashboard they land on). Authorization is **capability-based**, not role-based:
  - Owning a `creator_profiles` row → can publish skills.
  - Owning a license → can download the licensed skill version.
  - `is_admin` flag → access to moderation endpoints.
- Pure FastAPI dependencies (`Depends(...)`) for authz checks: `current_user`, `require_creator`, `require_admin`, `license_for_skill(skill_id)`.

---

## Email verification

- Required before publishing a skill, before purchasing, before issuing API tokens.
- Token is a single-use signed JWT (24h) sent to the registered email via the email provider (Resend or SES — pick at integration time).
- Login is allowed while unverified, but a top banner blocks gated actions.

---

## Sessions

- JWT contains `sub` (user_id), `email_verified`, `is_admin`, `iat`, `exp`, `jti`.
- Default lifetime: 7 days, sliding (refresh on activity, capped at 30 days total).
- Logout adds the `jti` to a Redis-backed denylist until natural expiry.
- Tokens are minted on login; do NOT include role in the JWT (role can change; re-fetch on each request from the user row).

---

## API token model (`api_tokens` table — not in core data model, define here)

| col | type | notes |
|---|---|---|
| id | uuid pk | |
| user_id | uuid fk → users.id | |
| name | text | display name set by user |
| token_hash | text | argon2id |
| prefix | text | first 8 chars of plaintext (for UI display) |
| scopes | text[] | `["skills:read", "skills:publish", "licenses:download"]` |
| last_used_at | timestamptz | nullable |
| created_at | timestamptz | |
| expires_at | timestamptz | nullable |
| revoked_at | timestamptz | nullable |

API tokens are checked via `Authorization: Bearer skg_live_xxx` header. Cookie auth is for browsers only; tokens are for CI / scripts.

---

## Rate limits (suggested starting points)

- Unauthenticated `/v1/auth/login` and `/v1/auth/forgot`: 10/min per IP, 50/hour per IP, exponential backoff on failures.
- Unauthenticated `/v1/auth/register`: 5/hour per IP.
- API token endpoints: 60/min per user.

Implement in middleware using `slowapi` (Redis-backed). Centralize limits in `apps/api/src/core/rate_limits.py`.

---

## Frontend integration

- Both Next.js apps share a `useUser()` hook in `packages/ui` that hits `/v1/auth/me` via the typed `api-client`.
- Sign-in / sign-up are server actions that proxy to FastAPI; cookies are set by the API and forwarded by Next via the response headers.
- A user with role=`buyer` lands on the marketplace home after login. role=`creator` lands on the creator dashboard. Admins see an "Admin" entry in the user menu.
- The "Become a creator" flow lives in the marketplace; it triggers Stripe Connect onboarding then redirects to the creator app.

---

## Security must-haves

- All passwords ≥ 12 chars; reject common-password list (use `zxcvbn` server-side score ≥ 3).
- CSRF: SameSite=Lax cookie + state-changing endpoints require `Origin` header check; double-submit token for cross-origin embeds (only the creator preview iframe needs this, defer to Phase 3).
- All `auth.*` actions log to `audit_log`.
- Account enumeration: `/forgot` always returns 200 regardless of whether the email exists.
- Login throttling: per-account counter in Redis; lock account for 15 min after 10 failed attempts in 10 min.

---

## Acceptance

- [ ] All endpoints listed above are live and covered by integration tests.
- [ ] Cookie auth works for both Next.js apps (verified by Playwright sign-in test).
- [ ] API token auth works against the `/v1/skills/me` endpoint (placeholder until skills module lands).
- [ ] OAuth flow works for Google in development with mocked provider.
- [ ] Email verification + password reset work end-to-end against mailhog locally.
- [ ] Audit log shows entries for register, login, logout, password reset, become-creator, token issue, token revoke.
