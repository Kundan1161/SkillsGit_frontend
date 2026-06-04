# Wave-2 Synthesis Report — Engineering / Testing & QA

**Niche:** engineering — testing-qa
**Date:** 2026-05-14
**Author agent:** Wave-2 methodology synthesis

## Files produced

All net-new skills. No existing testing-qa skill was found in `synth/`, so nothing was merged.

| File | Skill name | Sources |
|------|-----------|---------|
| `qa-test-strategy-planner.skills.md` | QA Test Strategy Planner | 7 |
| `qa-flaky-test-investigator.skills.md` | QA Flaky Test Investigator | 7 |
| `qa-e2e-test-suite-architect.skills.md` | QA E2E Test Suite Architect | 6 |
| `qa-property-based-test-designer.skills.md` | QA Property-Based Test Designer | 6 |
| `qa-mutation-coverage-reviewer.skills.md` | QA Mutation Coverage Reviewer | 7 |

All five are `license_type: free`, no pricing values, body in the 300-450 line target band, all required and recommended sections present, frontmatter conforming to `prompts/shared/skills-md-spec.md`.

## Sources reviewed (verified MIT / Apache-2.0 / BSD / ISC / Unlicense, >=100 stars, commit within 18 months)

| Repo | License | Stars | Last push |
|------|---------|-------|-----------|
| https://github.com/microsoft/playwright | Apache-2.0 | 88,708 | 2026-05-14 |
| https://github.com/cypress-io/cypress | MIT | 49,648 | 2026-05-14 |
| https://github.com/microsoft/playwright-mcp | Apache-2.0 | 32,510 | 2026-05-12 |
| https://github.com/dubzzz/fast-check | MIT | 4,937 | 2026-05-14 |
| https://github.com/stryker-mutator/stryker-js | Apache-2.0 | 2,868 | 2026-05-14 |
| https://github.com/BurntSushi/quickcheck | Unlicense | 2,756 | 2026-04-03 |
| https://github.com/infection/infection | BSD-3-Clause | 2,202 | 2026-05-14 |
| https://github.com/stryker-mutator/stryker-net | Apache-2.0 | 2,000 | 2026-05-14 |
| https://github.com/typelevel/scalacheck | BSD-3-Clause | 1,963 | 2026-05-10 |
| https://github.com/hcoles/pitest | Apache-2.0 | 1,818 | 2026-05-13 |
| https://github.com/boxed/mutmut | BSD-3-Clause | 1,293 | 2026-05-09 |
| https://github.com/pact-foundation/pact-jvm | Apache-2.0 | 1,129 | 2026-05-03 |
| https://github.com/pact-foundation/pact-go | MIT | 938 | 2026-05-14 |
| https://github.com/pact-foundation/pact-python | MIT | 667 | 2026-05-14 |
| https://github.com/muter-mutation-testing/muter | MIT | 551 | 2026-04-27 |
| https://github.com/ctrf-io/github-test-reporter | MIT | 349 | 2026-05-08 |
| https://github.com/pact-foundation/pact-js | MIT (verified at file scope; org-level shows NOASSERTION but the repo LICENSE is MIT) | 1,770 | 2026-05-14 |

## Patterns observed across sources

1. **Determinism is the load-bearing virtue.** Every healthy framework invests heavily in deterministic time, seeded randomness, isolated workers, and stable selectors. The flaky-test and e2e skills hammer this point.
2. **Page-objects favor action verbs over getter chains.** Modern frameworks promote `page.checkout.submit()` style over `page.findElement('#submit').click()`. Reflected in the e2e architect skill.
3. **Auto-wait > fixed sleeps.** Universally the best frameworks have made fixed sleeps a code smell. Encoded as an explicit anti-pattern.
4. **Mutation testing tools converge on the same mutators.** Boundary, negation, arithmetic, return, conditional, method-call. The mutation-coverage skill uses that exact taxonomy.
5. **Property-based libraries converge on the same anchor properties.** Round-trip, conservation, idempotence, oracle, anti-property. The property-based skill uses those families.
6. **Structured test reporting matters.** CTRF-style JSON or JUnit XML is the entry point for any dashboarding, flake tracking, or mutation re-scoring. Mentioned across multiple skills.
7. **Contract tests sit between unit and e2e.** Pact-style consumer-driven contracts catch schema drift that lower tests miss and upper tests catch only via expensive failure. The strategy-planner explicitly slots them.

## Rejections (licenses or staleness disqualified)

- **HypothesisWorks/hypothesis** — license `NOASSERTION` on GitHub API; not on allowed list. Excluded.
- **typelevel/proper** — GPL-3.0. Excluded.
- **flyingmutant/rapid** — MPL-2.0. Excluded.
- **mbj/mutant** — `NOASSERTION`. Excluded.
- **angular/protractor** — last push 2023-05; over 18 months stale. Excluded.
- **mull-project/mull** — Apache-2.0 and active, but C/C++-only and a poor cross-language exemplar; deprioritized in favor of broader-applicable tools.
- **stream_data (whatyouhide)** — license `null`. Excluded despite high activity.
- **jqwik-team/jqwik** — EPL-2.0; not on the allowed list (MIT/Apache-2.0/BSD/ISC/Unlicense only). Excluded.

## Confidence

**High** for the test-strategy-planner, flaky-test-investigator, and e2e-suite-architect skills — these synthesize patterns that converge cleanly across 5+ active sources.

**High** for the mutation-coverage-reviewer — the survivor taxonomy and prioritization rubric is well-supported across Stryker, pitest, infection, mutmut, and muter.

**Medium-high** for the property-based-test-designer — the methodology is well-supported but the body trades cross-framework generality for less code-specificity; teams may want a framework-targeted follow-up.

## Suggested follow-up niches

1. **Performance / load testing** — k6, Locust, Gatling, JMeter (license check needed) — a separate methodology with its own risk model (capacity planning, SLO setting, percentile interpretation).
2. **Accessibility testing** — axe-core, pa11y — a focused skill for converting axe reports into prioritized remediations.
3. **Test-data management** — factory-bot-style builders, anonymization, seeding strategies — adjacent to but distinct from any of the five skills here.
4. **Contract-testing implementer** — a deeper Pact-specific skill that converts an API spec into producer/consumer contracts; currently only referenced in the strategy-planner.
5. **Visual regression testing** — Percy/Chromatic-style visual diff strategies, baseline management, deterministic-environment setup. A niche but high-value area for teams that have a maintainable budget for it.
6. **CI test-runtime optimizer** — orthogonal to the five skills here; focused on shard balancing, cache strategies, and dependency-graph-based test selection.

## Notes for integration

- All skills emit `claude-opus-4-7` as required model and Sonnet/4o/4.1 as compatible.
- All five share the `niche:testing-qa` first tag.
- No trademarks used as methodology names — references to Pact, Stryker, fast-check, pitest, etc. appear only in source citations and as tool names in the body, not as methodology branding.
- All sources verified for license_type, star count, and recent commit via the GitHub search API on the date above.
