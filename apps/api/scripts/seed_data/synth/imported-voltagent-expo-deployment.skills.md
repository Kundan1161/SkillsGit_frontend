---
id: skillsgit-curated/imported-voltagent-expo-deployment
version: 1.0.0
name: Expo Deployment with EAS
description: Deploy Expo applications across iOS, Android, and Web using EAS (Expo Application Services) — builds, store submissions, EAS Hosting, and CI/CD workflows.
authors:
  - name: Expo
    handle: expo
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, expo, eas, deployment, testflight, app-store, play-store]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [eas build, expo deploy, testflight, app store submit, play store submit, eas hosting]
example_invocations:
  - Build and submit my Expo app to TestFlight
  - Set up EAS Hosting deploys for PR previews
  - Configure eas.json for production builds
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Expo Deployment

This skill covers deploying Expo applications across all platforms using EAS (Expo Application Services).

## When to use

Use this skill when shipping iOS, Android, or Web builds of an Expo app — configuring `eas.json`, submitting to TestFlight or Play Store internal tracks, running `eas deploy` for web, or wiring up CI/CD with EAS Workflows.

## How to apply

Install the EAS CLI, initialize EAS, configure profiles in `eas.json`, run `eas build` for native, `eas deploy` for web, and `eas submit` for store submissions. Use `appVersionSource: "remote"` so EAS owns version numbers.

## Quick Start

```bash
npm install -g eas-cli
eas login
npx eas-cli@latest init
```

`init` creates `eas.json` with build profiles.

## Build Commands

```bash
# iOS App Store
npx eas-cli@latest build -p ios --profile production

# Android Play Store
npx eas-cli@latest build -p android --profile production

# Both platforms
npx eas-cli@latest build --profile production
```

## Submit to Stores

```bash
# iOS (build + submit)
npx eas-cli@latest build -p ios --profile production --submit

# Android (build + submit)
npx eas-cli@latest build -p android --profile production --submit

# Shortcut for iOS TestFlight
npx testflight
```

## Web Deployment (EAS Hosting)

```bash
npx expo export -p web
npx eas-cli@latest deploy --prod      # production
npx eas-cli@latest deploy             # PR preview
```

## EAS Configuration (`eas.json`)

```json
{
  "cli": {
    "version": ">= 16.0.1",
    "appVersionSource": "remote"
  },
  "build": {
    "production": {
      "autoIncrement": true,
      "ios": { "resourceClass": "m-medium" }
    },
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

## Platform Notes

### iOS

- Use `npx testflight` for quick TestFlight submissions.
- Configure Apple credentials via `eas credentials`.

### Android

- Set up Google Play Console service account.
- Use tracks in order: internal → closed → open → production.

### Web

- EAS Hosting provides preview URLs for PRs.
- Production deploys to your custom domain.

## Automated Deployments (EAS Workflows)

```yaml
# .eas/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  build-ios:
    type: build
    params:
      platform: ios
      profile: production

  submit-ios:
    type: submit
    needs: [build-ios]
    params:
      platform: ios
      profile: production
```

## Version Management

With `appVersionSource: "remote"` EAS owns versions:

```bash
eas build:version:get
eas build:version:set -p ios --build-number 42
```

## Monitoring

```bash
eas build:list
eas build:view
eas submit:list
```

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `expo/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-deployment (MIT)
