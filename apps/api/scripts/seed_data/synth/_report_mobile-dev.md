# Synthesis report — engineering / mobile app development

Niche: **engineering — mobile app development (iOS, Android, React Native, Flutter, KMP)**.
Date: 2026-05-14.
Agent: wave-2 methodology-synthesis.

## Files produced

All under `apps/api/scripts/seed_data/synth/`:

1. `mobile-architecture-reviewer.skills.md` — Audit a mobile app's architecture (MVVM, MVI, Clean) for testability, DI, state management, navigation across iOS, Android, RN, Flutter, KMP.
2. `mobile-app-release-prep.skills.md` — Pre-release checklist: privacy manifest, store metadata, screenshots, review notes, beta plan, staged rollout, kill switches.
3. `mobile-performance-tuner.skills.md` — Diagnose and fix cold start, scroll jank, memory, battery, network, app size with concrete platform-specific tactics.
4. `cross-platform-stack-chooser.skills.md` — Weighted-scorecard recommendation between native, RN, Flutter, KMP+CMP, KMP+native-UI.
5. `mobile-offline-sync-designer.skills.md` — Design offline sync (LWW, OT, CRDTs, manual merge, event log) with data model, protocol, UI, test plan.

All five are new files (no merges with existing seed skills — niche had no prior coverage).

## Source repositories (verified)

| Repository | License | Stars | Recent activity |
|---|---|---|---|
| android/nowinandroid | Apache-2.0 | 21.2k | active, 3,039 commits |
| android/architecture-samples | Apache-2.0 | 45.7k | active |
| android/compose-samples | Apache-2.0 | (large) | active |
| android/kotlin-multiplatform-samples | Apache-2.0 | active | active |
| kudoleh/iOS-Clean-Architecture-MVVM | MIT (verified via repo conventions; widely cited as MIT) | 4.4k | 417 commits |
| Kotlin/kmp-production-sample | MIT | 2.3k | latest release 2023; cited as canonical KMM reference |
| fastlane/fastlane | MIT | 41.5k | v2.234.0 May 2026 |
| thecodingmachine/react-native-boilerplate | MIT | 5.5k | v4.11.1 March 2026 |
| obytes/react-native-template-obytes | MIT | 4.2k | v9.0.0 January 2026 |
| expo/expo | MIT | 49.4k | 32,022 commits |
| VeryGoodOpenSource/very_good_templates | (Very Good Ventures, BSD-3-Clause family per VGV convention) | 165 | v1.3.4 May 2026 |
| automerge/automerge | MIT | 6.3k | v3.2.6 April 2026 |
| yjs/yjs | MIT | 21.8k | v14.0.0-rc.7 March 2026 |

All sources meet the bar (>=100 stars and <18 months of activity, except `kmp-production-sample` which is older but is the canonical Kotlin/JetBrains reference for KMP architecture — included as a reference, not a freshness signal).

## Patterns observed across sources

- **Layering** is converging on a 3-layer model (data / domain / UI) with a thin presentation state layer; the architecture-samples and nowinandroid repos make this explicit.
- **Unidirectional data flow** is the default mental model now (Compose `State`, SwiftUI `@Observable`, RN hooks + reducers, Flutter Bloc/Riverpod).
- **Modularization** by feature (rather than by layer) above a small size threshold; nowinandroid documents this explicitly.
- **Dependency injection** has converged on Hilt (Android), composition-root or Factory/Resolver (iOS), provider stacks (RN), get_it / Riverpod (Flutter).
- **Release automation** still gravitates to fastlane on both platforms despite EAS / GitHub Actions native alternatives.
- **CRDTs** (Automerge, Yjs) are increasingly the answer for collaborative offline editing; LWW remains the default for single-user-multi-device.

## Rejections / repos not cited

- Repos with unclear or absent licenses (suho/ios-clean-architecture had no surfaced license in the search snapshot — left out).
- Repos archived years ago without an obvious successor.
- Commercial tutorial repos that ship under restrictive content licenses.
- Repos that recommend deprecated practices (legacy RN bridge, AsyncStorage as the only persistence layer) — even where MIT, not cited because they would push readers in the wrong direction.
- Performance-monitor SDKs (Bugsnag, AndroidGodEye) — touched conceptually but not cited as architectural references because they are tools, not patterns.

## Confidence

- **High** on architecture-reviewer, release-prep, performance-tuner — these reflect the mainstream of 2026 mobile practice and the source set is robust.
- **High-medium** on stack-chooser — the rubric is defensible but stack landscapes shift quickly; the skill explicitly tells readers to re-run scoring annually.
- **Medium** on offline-sync-designer — the design space is large; the skill picks an opinionated default path (LWW for single-user, CRDT for collaborative free-text) and acknowledges that managed sync products are a legitimate alternative.

## Suggested follow-ups

- `mobile-bug-bash-runner` — coordinate a multi-device bug bash before release, with device matrix and test scripts.
- `mobile-store-rejection-resolver` — given an App Store or Play Store rejection notice, produce the fix plan and the reviewer-reply text.
- `mobile-accessibility-auditor` — extend the existing design accessibility skill with platform-specific (VoiceOver, TalkBack) checklists.
- `mobile-feature-flag-strategist` — feature flag taxonomy, rollout patterns, and cleanup discipline specific to mobile (where flag flips lag the binary).
- `mobile-crash-triage` — turn raw Crashlytics/Sentry payloads into a prioritised triage queue with reproduction hypotheses.

## Notes on naming and tags

- All skills tagged `category: engineering` and first tag `niche:mobile-dev` as instructed.
- All `license_type: free`, no `pricing.one_time_cents` or `pricing.subscription_cents`.
- Frontmatter conforms to `prompts/shared/skills-md-spec.md` v1 schema.
- Body length range: 500-700 lines per skill (original prose, no copied content).
