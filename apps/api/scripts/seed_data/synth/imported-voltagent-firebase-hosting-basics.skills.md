---
id: skillsgit-curated/imported-voltagent-firebase-hosting-basics
version: 1.0.0
name: Firebase Hosting (Classic) Basics
description: Deploy static sites, SPAs, and microservices with Firebase Hosting Classic — global CDN, SSL, preview channels, GitHub integration, and dynamic content via Cloud Functions or Cloud Run.
authors:
  - name: Firebase
    handle: firebase
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, firebase, hosting, cdn, static-site, deploy]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [firebase hosting, firebase deploy, static site, preview channel, firebase.json]
example_invocations:
  - Deploy my SPA to Firebase Hosting
  - Set up preview channels for PR review
  - Configure firebase.json with redirects and headers
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Firebase Hosting (Classic) Basics

## When to use

Use this skill for deploying **static** web apps, SPAs, and microservices with Firebase Hosting Classic. **Do NOT use for Firebase App Hosting** (full-stack frameworks with SSR — use the App Hosting skill).

## How to apply

Configure via `firebase.json`. Use preview channels for PR review. Use Cloud Functions or Cloud Run for dynamic routes. Test locally with the emulator before deploy.

## Capabilities

- Production-grade web content hosting.
- Global CDN caching.
- Built-in SSL.
- Preview channels for testing changes.
- GitHub integration.
- Dynamic content via Cloud Functions or Cloud Run.

## When to Choose Firebase Hosting (Classic)

- Static sites
- Simple SPAs without server-side rendering
- CLI-based build control

If you're using full-stack frameworks like Next.js or Angular with SSR, choose **Firebase App Hosting** instead.

## Setup

Configuration happens via `firebase.json`. Reference files cover:

- **configuration.md** — `firebase.json` schema, rewrites, headers, redirects.
- **deploying.md** — deployment workflows and CI/CD.

## Local Testing

```bash
npx -y firebase-tools@latest emulators:start --only hosting
```

## Typical firebase.json

```json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [{ "source": "**", "destination": "/index.html" }],
    "headers": [
      {
        "source": "/assets/**",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
      }
    ]
  }
}
```

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `firebase/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/firebase/skills/tree/main/skills/firebase-hosting-basics (Apache-2.0)
