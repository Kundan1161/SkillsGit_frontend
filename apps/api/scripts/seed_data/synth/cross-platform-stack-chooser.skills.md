---
id: skillsgit-curated/cross-platform-stack-chooser
version: 1.0.0
name: Cross-Platform Mobile Stack Chooser
description: Given product, team, and runtime constraints, recommend native iOS+Android, React Native, Flutter, or Kotlin Multiplatform with weighted trade-offs and a written rationale.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags: [niche:mobile-dev, technology-selection, react-native, flutter, kotlin-multiplatform, native-ios, native-android, decision-framework]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 8000
trigger_keywords:
  - choose mobile stack
  - native vs react native
  - native vs flutter
  - flutter vs react native
  - kmp vs flutter
  - compose multiplatform vs flutter
  - cross platform recommendation
  - mobile tech selection
  - mobile architecture choice
  - which mobile framework
  - rebuild app stack
  - new app stack
example_invocations:
  - "We're a four-engineer startup building a fitness app with Bluetooth peripherals. Should we go native, RN, Flutter, or KMP?"
  - "Our two-platform team is considering rewriting our React Native app in Flutter. Make the case both ways."
  - "Stack recommendation for a regulated banking app, twelve engineers, three-year horizon."
inputs:
  - name: product_summary
    type: text
    required: true
    description: What the app does, who uses it, and what the next twelve months look like. One paragraph minimum.
  - name: team_composition
    type: text
    required: true
    description: Headcount, existing skills (iOS, Android, web/React, Dart/Flutter, Kotlin), hire plans, and budget signals.
  - name: must_have_features
    type: text
    required: false
    description: Anything that constrains the choice — Bluetooth, ARKit/ARCore, video editing, large file handling, deep OS integration, accessibility certifications.
  - name: time_horizon
    type: choice
    required: false
    description: How long the codebase needs to live. Defaults to "2-3 years".
    choices: [under-6-months, 6-12-months, 1-2-years, 2-3-years, 3-5-years, indefinite]
  - name: platforms
    type: choice
    required: false
    description: Target platforms. Defaults to "ios-and-android".
    choices: [ios-only, android-only, ios-and-android, ios-android-web, ios-android-desktop, all]
  - name: risk_appetite
    type: choice
    required: false
    description: How much new-tech risk the team can absorb. Defaults to "balanced".
    choices: [conservative, balanced, willing-to-experiment]
outputs:
  - name: recommendation
    type: markdown
    description: Primary recommendation with rationale, runner-up, and a short list of reasons the choice could be wrong.
  - name: trade_off_matrix
    type: markdown
    description: Weighted scoring table across native iOS+Android, React Native, Flutter, KMP+Compose Multiplatform, and an "all native" baseline.
  - name: migration_or_starter_notes
    type: markdown
    description: If the team has an existing codebase, how to migrate. If starting fresh, the first month's setup plan.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# Cross-Platform Mobile Stack Chooser

## When to use

Use this skill when a team is at a stack inflection point: starting a new app, considering a rewrite, planning a third platform, or evaluating whether to keep an existing stack as it scales. The question is rarely "which framework is best" — it is "which framework fits this product, this team, and this horizon." A good recommendation is defensible, not absolute.

Typical triggers:

- Greenfield mobile app at a company that has both web and mobile concerns.
- An iOS-only team being asked to ship Android within the year.
- A React Native team feeling the limits of the bridge or paying a permanent native-modules tax.
- A native team being asked to add a web client and wondering about Compose Multiplatform or Flutter web.
- A founder asking "should we use Flutter?" with no surrounding context.

Do not use it for:

- Choosing a state-management library or UI kit within an already-chosen stack; that is a smaller decision and the architecture reviewer covers it indirectly.
- Picking between hosted backend providers; out of scope.
- Deciding whether to outsource development; that is a vendor selection problem, not a stack problem.

## Inputs

- `product_summary` (required) — A product paragraph. Constraints differ enormously between "a content reader" and "a peer-to-peer video calling app." Without this, the recommendation collapses into a generic comparison.
- `team_composition` (required) — Existing skills dominate the answer. Telling a five-person all-iOS team to ship in Flutter ignores the human capital cost.
- `must_have_features` — Capabilities that some stacks struggle with: Bluetooth LE, ARKit/ARCore, video pipelines, MDM, accessibility audits, Apple Watch / Wear OS, CarPlay / Android Auto, Live Activities.
- `time_horizon` — A six-month proof of concept and a five-year regulated app deserve different answers.
- `platforms` — Tablet support, web, desktop, watch, automotive, foldable. Adding surfaces compounds the cost of native.
- `risk_appetite` — Conservative teams should not bet on stacks that have shipped one major version this year; willing-to-experiment teams can.

## How to apply

The recommendation is built from a weighted scorecard, then sanity-checked with two falsification questions, then written up so the reader can see how to disagree.

### 1. Establish the criteria and weights

Use a shared seven-criterion rubric. Adjust weights based on the inputs.

| Criterion | Default weight | Adjust upward when |
|---|---|---|
| Team fit (existing skills, hiring market) | 25 | Small team or fixed budget |
| Feature reach (capability coverage on both platforms) | 20 | Must-haves include deep OS integration |
| Performance and UX fidelity (60 fps default, native feel) | 15 | App is graphics-heavy or premium positioning |
| Time to first shippable build | 15 | Time horizon is under 12 months |
| Long-run maintainability (ecosystem health, hiring) | 10 | Time horizon is 3+ years |
| Toolchain quality (debugging, profiling, CI) | 10 | Team values fast iteration |
| Code reuse with other surfaces (web, desktop, backend) | 5 | The product targets web + mobile or has a strong backend in the same language |

If the inputs include "highly regulated" or "must pass a security audit", add an eighth criterion: supply-chain risk (weight 10) and rebalance the others.

### 2. Score the candidates

The candidate set is:

- **Native iOS + Native Android** — Swift/SwiftUI and Kotlin/Jetpack Compose, two codebases.
- **React Native (new architecture)** — Fabric + TurboModules, Hermes, TypeScript, with native modules where needed.
- **Flutter** — Dart, Skia/Impeller rendering, single codebase with platform channels.
- **Kotlin Multiplatform with Compose Multiplatform** (KMP+CMP) — shared Kotlin logic, shared or native UI.
- **Kotlin Multiplatform with native UI** (KMP-native-UI) — shared Kotlin business logic; SwiftUI for iOS, Compose for Android.

For each candidate, assign a 0–5 score per criterion. The skill follows a shared default for each cell, then adjusts per input. Defaults below reflect the state of the ecosystem as of mid-2026 and are intentionally moderate.

| Criterion | Native | React Native | Flutter | KMP+CMP | KMP+native UI |
|---|---|---|---|---|---|
| Team fit | depends | high for React/JS teams | depends on Dart skill | high for Kotlin teams | high for native teams |
| Feature reach | 5 | 4 | 4 | 4 | 5 |
| Performance / UX fidelity | 5 | 4 | 4 (5 with Impeller) | 4 | 5 |
| Time to first shippable build | 2 | 4 | 4 | 3 | 3 |
| Long-run maintainability | 5 | 3 | 4 | 3 | 4 |
| Toolchain quality | 5 | 4 | 4 | 4 | 4 |
| Code reuse | 1 | 4 (RN web) | 4 (Flutter web/desktop) | 4 (CMP web/desktop) | 3 (logic only) |

These are not gospel; they are starting points the skill adjusts. For example, if `must_have_features` includes "Live Activities and Dynamic Island", drop Flutter's feature-reach score by one because the native bridge work to fully match is non-trivial. If the team already has a 200k-line web React codebase, lift React Native's team-fit by one.

### 3. Apply per-input adjustments

A short list of common adjustments:

- **Tiny team (≤ 3 engineers)** for a consumer app → favour Flutter or RN; cut native by one on time-to-first-build and team-fit.
- **iOS-first audience with premium positioning** (a music app, a creative tool) → favour native; the long-tail "feels native" gap is hardest to close on cross-platform.
- **Heavy Bluetooth, ML, audio, or video pipeline** → favour native or KMP+native-UI; cross-platform wrappers exist but you will eventually need native code for one platform's quirks.
- **Web React app with shared brand and behaviour** → favour React Native; the JSX/TSX mental model and shared component patterns reduce learning cost.
- **Existing Android team adding iOS** → favour KMP+CMP or KMP+native-UI; the team can reuse domain knowledge without learning a new language.
- **Regulated industry, 5-year horizon** → favour native; framework deprecation is the largest long-term risk and you can predict native APIs farther out.
- **AR/3D-heavy** → favour native; ARKit and ARCore are well supported through wrappers, but 3D rendering ecosystems are richer natively.
- **Heavy enterprise MDM and SSO** → favour native; MDM SDKs land on iOS and Android first.
- **AR Glasses, automotive, watch, TV** → favour native; cross-platform support for these surfaces is partial and lags the main platforms.
- **Fast user-facing iteration, push UI updates to users** → favour RN; CodePush-style flows are easier on RN than on Flutter or native.

### 4. Tally the weighted score

Multiply each cell by its criterion weight, sum, and rank candidates. The top two are the recommendation and the runner-up; if the difference is within 5%, present both as viable and lean on the falsification questions in step 5 to break the tie.

### 5. Run two falsification questions

Before locking the recommendation, ask:

5.1. **What evidence would change this answer in six months?** If the answer is "almost anything," the recommendation is fragile and should be presented as a hypothesis. If it is "only a major team-composition change", the recommendation is stable.

5.2. **What is the worst plausible outcome with this choice?** Examples: the chosen framework releases a backward-incompatible major version; the in-house champion leaves; a critical SDK does not ship a binding for the framework. For each candidate, name the failure mode and the team's exit plan.

A recommendation that cannot survive these two questions is reworded as a smaller bet — e.g., "build the next feature in Flutter as a contained module to test the choice before betting the codebase."

### 6. Write the recommendation

The document is short on purpose:

- **Recommendation** — one paragraph naming the choice, with the headline reason.
- **Runner-up and when to pick it instead** — one paragraph.
- **Risks specific to this choice** — bullets.
- **First-month plan** — a numbered list of what the team does in week 1 through week 4.
- **The scorecard appendix** — the table with the adjusted weights.

The reader should be able to disagree with the recommendation by changing a weight, not by introducing new facts.

### 7. Account for migration cost

If the team has an existing codebase, the recommendation is constrained by sunk and switching cost. Apply this rule of thumb:

- A migration is worth it when the criteria score for the new stack exceeds the current stack's score by at least 25% of the maximum after the migration cost is amortised across the time horizon.
- Amortised cost = engineer-months of migration ÷ time horizon in months ÷ team size.
- Below 25%, recommend modernising the current stack (RN upgrades, Compose adoption inside a View app, KMP-on-the-side, etc.) rather than rewriting.

Migrations also have hybrid options worth surfacing:

- Adopt KMP gradually under an existing native app for shared domain logic.
- Start a new feature in a native module that the existing RN app embeds, while keeping the rest in JS.
- Adopt Compose progressively in a View-based Android app and SwiftUI progressively in a UIKit iOS app; this is rarely a "stack" decision in 2026 because both are now standard within their platforms.

### 8. Style notes

- Do not write the recommendation in absolute terms. Use "leads", "fits", "tends to be cheaper" rather than "is best".
- Cite the rubric in the rationale so the reader can argue with the inputs.
- Avoid making prediction claims about which framework will exist in five years. Predict only what the team can verify in three months.

## Outputs

`recommendation` is the short prose document.

`trade_off_matrix` is the weighted scorecard with the adjustments applied.

`migration_or_starter_notes` is the first-month plan or the migration plan, depending on whether the team has an existing codebase.

## Examples

### Example: fitness app, four-engineer startup, Bluetooth peripherals, 2-3 year horizon

Excerpt from `recommendation`:

```
Recommendation: React Native on the New Architecture (Fabric + TurboModules)
with Hermes, plus a thin native module for the Bluetooth LE flow that
handles your heart-rate strap.

Headline reason: three of your four engineers have shipped React or
React Native before, so team-fit dominates the scorecard. The 2-3 year
horizon is comfortably inside RN's recent stability arc, and you can
share UI patterns with the marketing site you mentioned. The Bluetooth
flow is the one place you will write native code — a TurboModule per
platform is roughly two engineer-weeks of work and you only do it once.

Runner-up: Flutter. Pick it instead if the team is willing to learn Dart
and you want a tighter visual identity (custom design system) than the
default RN component look. The score gap is 8% in RN's favour, mostly
on team-fit; that gap closes if your Android developer is keen on Dart
and learns it on the side.

Risks specific to this choice:
- TurboModule complexity for BLE; have one engineer specialise here.
- RN dependency churn means a yearly upgrade ritual; budget one week per
  major-version upgrade and pin your transitive deps.
- Push-update flows (CodePush, EAS Update) bypass app-store review;
  understand the policy before relying on them.

First-month plan:
  Week 1: scaffold with the New Architecture, Hermes, TypeScript, EAS
          build pipeline, basic CI.
  Week 2: design system pass — pick a component library (Tamagui or
          React Native Paper), set up tokens, theme.
  Week 3: BLE TurboModule on iOS first; integrate with a real strap.
  Week 4: BLE TurboModule on Android; ship internal alpha.
```

### Example: regulated banking app, twelve engineers, three-year horizon

Excerpt from `recommendation`:

```
Recommendation: native iOS (SwiftUI primarily, UIKit interop where needed)
and native Android (Jetpack Compose, View System for complex legacy
screens). Use Kotlin Multiplatform for the shared business logic layer
(crypto helpers, request signing, fraud heuristics, model classes).

Headline reason: in a regulated three-year horizon, supply-chain
predictability and the depth of platform-specific security tooling
(SafetyNet/Play Integrity, App Attest, Apple's DeviceCheck, secure
enclave APIs) dominate. Native scores 5 on feature reach and long-run
maintainability; cross-platform candidates score 3-4 because at least
one critical SDK trails on every release.

Runner-up: KMP-with-native-UI. Score gap is 4%; pick it if you want
maximum code reuse for business logic and can spare a Kotlin specialist
to maintain the shared module.

Risks specific to this choice:
- Two codebases to staff. Hiring plan must account for both.
- Feature parity drift between iOS and Android is the most common
  failure mode; address with an explicit cross-platform PM and shared
  acceptance criteria per release.
- The shared KMP module is a third codebase; size it small (no UI logic).

First-month plan:
  Week 1: hire / assign two tech leads (iOS lead, Android lead).
          Draft the module boundaries and the KMP scope (what is shared,
          what is not).
  Week 2: set up Bazel or Gradle + SwiftPM with KMP integration. CI
          on internal hardware.
  Week 3: ship a hello-world "card balance" screen end to end on both
          platforms using the shared KMP module.
  Week 4: security review of the build pipeline; threat-model the KMP
          shared module's exposure surface.
```

## Limitations

- The rubric encodes mid-2026 ecosystem health. Re-run the scoring annually; weights change as frameworks mature or stall.
- The skill does not predict whether a framework will exist in five years; it sizes the risk and asks the team to plan for exit.
- The recommendation is only as good as the inputs. Vague team or product descriptions yield vague recommendations; push back for specifics.
- "Just use what your team knows" is sometimes the right answer; the skill should not invent a more interesting choice for sport.
- The migration-cost math is rough; teams with idiosyncratic codebases should validate the amortisation assumption against a small spike before committing.

## Sources reviewed

- https://github.com/android/nowinandroid
- https://github.com/Kotlin/kmp-production-sample
- https://github.com/android/kotlin-multiplatform-samples
- https://github.com/thecodingmachine/react-native-boilerplate
- https://github.com/obytes/react-native-template-obytes
- https://github.com/VeryGoodOpenSource/very_good_templates
- https://github.com/expo/expo
- https://github.com/kudoleh/iOS-Clean-Architecture-MVVM
