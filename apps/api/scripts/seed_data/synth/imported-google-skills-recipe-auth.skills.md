---
id: skillsgit-curated/imported-google-skills-recipe-auth
version: 1.0.0
name: Google Cloud Authentication Recipe
description: Authenticate and authorize to Google Cloud services — human users, service identities, ADC, Workload Identity Federation, and best practices for secure access.
authors:
  - name: Google (original)
    handle: google
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-google, gcp, iam, authentication, adc, workload-identity]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gemini-2.0-pro]
trigger_keywords: [gcp auth, adc, service account, workload identity federation, gcloud auth, impersonation]
example_invocations:
  - "Authenticate a local Python script to a Google Cloud API."
  - "Set up Workload Identity Federation for code running on AWS."
  - "Use service account impersonation instead of downloading a key."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from google/skills under Apache-2.0.
---

# Authenticating to Google Cloud

## When to use

Use this skill when you need expert guidance on authenticating and authorizing to Google Cloud services and APIs — for human users, service identities, Application Default Credentials (ADC), and best practices for secure access.

## How to apply

Clarify who is authenticating, where the code runs, the target API, and which client library is in use. Recommend ADC + impersonation for local development, attached service accounts for in-cloud workloads, Workload Identity Federation for external workloads, and OIDC ID tokens for custom-app calls. Never recommend downloading service-account keys.

## Authentication

Authentication is the process of proving who you are. In Google Cloud, you represent a Principal (an identity like a user or a service). This is the first step before Authorization (determining what you can do).

### Clarifying Questions

1. Who or what is authenticating? (Human developer, local script, or production application?)
2. Where is the code running? (Local laptop, Compute Engine, GKE, Cloud Run, AWS/Azure?)
3. What is the target? (A Google Cloud API like Storage/BigQuery, or a custom application you built?)
4. Are you using a high-level client library? (Python, Go, Node.js libraries usually handle ADC automatically.)

## Human Authentication

Google Cloud supports several user identity configurations:
- Google-Managed Accounts (Cloud Identity / Google Workspace)
- Federation using Cloud Identity or Google Workspace (synced via GCDS)
- Workforce Identity Federation (syncless, attribute-based SSO via external IdP)

Access methods for developers and admins:
- Google Cloud Console
- gcloud CLI (`gcloud auth login`)
- Local Development with ADC (`gcloud auth application-default login`)
- Service Account Impersonation — preferred over downloading keys

For end users / customers of your apps: Identity-Aware Proxy (IAP) or Identity Platform (CIAM).

## Service-to-Service Authentication

When code runs in production, use a Service Account rather than a human user account.

- Service Account: a special identity for non-human users with its own email address.
- Service Agent: a Google-managed service account that lets services like Pub/Sub access resources on your behalf.

Best practice: attach a service account to the resource. The environment provides a short-lived token via the local metadata server. Do this on Compute Engine, Cloud Run, and similar resources.

### Special Cases

- GKE: use Workload Identity Federation for GKE to map Kubernetes identities to IAM principals.
- External workloads (AWS, Azure, on-prem): use Workload Identity Federation to exchange external tokens for short-lived Google Cloud access tokens.
- API keys: for public data or simplified access like Vertex AI Express Mode. Always restrict them to specific APIs/projects and store them in Secret Manager.
- OAuth 2.0 access scopes: legacy Compute Engine/GKE feature; check scopes if an attached service account fails despite correct IAM.
- Short-lived credentials: use the IAM Service Account Credentials API for impersonation, OIDC tokens, and self-signed JWTs.

## Authorization

After authentication, Google Cloud uses IAM to determine what the authenticated principal can do.

- Allow Policy: binds a Principal to a Role on a Resource.
- Predefined Roles (e.g., `roles/storage.objectViewer`) — always try these first.
- Custom Roles: user-defined permission collections when predefined roles are too broad.

## Examples

### Human-to-Service (Local Python Development)
1. Run `gcloud auth application-default login` to create local credentials.
2. Grant your email `roles/storage.objectViewer` on a bucket.
3. Use Python `storage.Client()` — ADC search order: `GOOGLE_APPLICATION_CREDENTIALS`, local gcloud JSON, attached service-account metadata.

### Service-to-Service (Cloud Run to Cloud SQL)
1. Attach a custom Service Account to your Cloud Run service.
2. Grant `roles/cloudsql.client` to that Service Account.
3. The Cloud Run environment provides the token automatically.

### Calling a Custom Application (OIDC)
When calling a private Cloud Run service from another service, the caller generates a Google-signed OIDC ID Token and passes it in the `Authorization: Bearer <TOKEN>` header.

## Validation Checklist

- [ ] User running code locally? Suggest `gcloud auth application-default login` or Service Account Impersonation.
- [ ] User attempting to use Service Account keys locally? Strongly discourage; recommend impersonation.
- [ ] User running in production? Recommend attaching a custom least-privilege service account.
- [ ] User relying on the Compute Engine default service account? Recommend creating a custom service account instead.
- [ ] User running on another cloud? Recommend Workload Identity Federation.
- [ ] User calling a custom app? Recommend OIDC ID Tokens.
- [ ] User restricted their API Keys? Check for appropriate API Key Restrictions.

## References

- Authentication Overview: https://docs.cloud.google.com/docs/authentication
- User Identities: https://docs.cloud.google.com/iam/docs/user-identities
- Application Default Credentials: https://docs.cloud.google.com/docs/authentication/provide-credentials-adc
- Service Account Best Practices: https://docs.cloud.google.com/iam/docs/best-practices-service-accounts

## Attribution

This skill was imported from `google/skills` under the Apache-2.0 license. Original content authored by Google. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections; addition of `## When to use` and `## How to apply` stubs required by our validator. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed

- https://github.com/google/skills/tree/main/skills/cloud/google-cloud-recipe-auth (Apache-2.0)
