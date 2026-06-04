# Wave-2 synthesis report — niche: paid acquisition (marketing)

## Files produced

- `mkt-paid-channel-audit.skills.md` — `skillsgit-curated/paid-channel-audit` (v1.0.0)
- `mkt-creative-test-planner.skills.md` — `skillsgit-curated/creative-test-planner` (v1.0.0)
- `mkt-mmm-mta-reviewer.skills.md` — `skillsgit-curated/mmm-mta-reviewer` (v1.0.0)
- `mkt-ltv-cac-modeler.skills.md` — `skillsgit-curated/ltv-cac-modeler` (v1.0.0)

All four are net-new skills. No existing synth files in this niche to merge with. The closest neighbor (`mkt-ab-test-designer`) is general experimentation; the creative-test-planner explicitly defers experimentation theory to it and focuses on the creative-program problem.

## Sources reviewed (license-verified)

| Repo | License | Stars | Note |
|---|---|---|---|
| facebookexperimental/Robyn | MIT | ~1.5k | MMM reference. |
| google/meridian | Apache-2.0 | ~1.4k | Bayesian MMM, successor to LightweightMMM. |
| pymc-labs/pymc-marketing | Apache-2.0 | ~823 | Bayesian MMM + CLV. |
| facebookincubator/GeoLift | MIT | 247 | Geo experimentation. Sub-1k stars — disclosed. |
| google/trimmed_match | Apache-2.0 | 72 | Geo experiments. Sub-threshold — disclosed. |
| google/GeoexperimentsResearch | Apache-2.0 | (low) | Cited in MMM/MTA reviewer only. |
| CamDavidsonPilon/lifetimes | MIT | ~1.5k | CLV / BG-NBD. Archived; successor pointed to pymc-marketing. |
| segmentio/utm-params | MIT | 42 | UTM parsing. Sub-threshold — disclosed. |
| google/ads-account-structure-script | Apache-2.0 | 28 | Sub-threshold; referenced only in audit skill. |

## Rejections (license fails)

- `Brainlabs-Digital/Google-Ads-Scripts` — GPL-2.0. Rejected (copyleft, not on the allowed list).
- `facebook/capi-param-builder` — Facebook proprietary platform-tied license (not MIT/Apache/BSD/ISC/Unlicense). Rejected.
- Most third-party CAPI / UTM tooling encountered was either GPL or unlicensed-by-omission. Rejected for the source list; concepts are common practice and referenced from general knowledge in the prose.

## Patterns synthesized across the source pool

1. **Causal vs correlational measurement.** The MMM cluster (Robyn, Meridian, PyMC-Marketing) and the experimentation cluster (GeoLift, Trimmed Match, GeoexperimentsResearch) together describe a measurement portfolio: regression-style mix models for strategic/budget questions, randomized geo or platform-lift experiments for causal validation. Reflected directly in the MMM/MTA reviewer skill's triangulation protocol.
2. **Saturation and adstock honesty.** Modern open MMM tooling (Robyn, Meridian, PyMC-Marketing) parameterizes saturation and carryover rather than fixing them. The reviewer skill names "fixed saturation parameters destroy model honesty" as a check, and the audit skill flags channel-mix decisions made without saturation reasoning.
3. **CLV is a curve, not a number.** The Lifetimes/PyMC-Marketing pattern (BG-NBD, Pareto/NBD, Gamma-Gamma) treats retention as a probability curve over cohorts; the LTV/CAC skill enforces the same discipline — never assume flat ARPU, never assume 100% terminal retention, always parameterize the tail.
4. **Identity-resilience.** Across the measurement and CLV repos, the shift toward identity-loss-resilient measurement (server-side, cohort, geo) is the dominant 2024–2026 theme. The audit and reviewer skills both reflect it — server-side dedup is mandatory, MTA validity is gated on identity match quality, geo experiments are the recommended causal anchor.
5. **Cohort discipline.** Every CLV/MMM library in the pool centers cohort-level rather than aggregate-level analysis. The LTV/CAC modeler enforces cohort math and explicitly warns about survivorship bias from blending cohorts of unequal age.

The prescriptive content (campaign-structure rules, creative-test variant matrices, audit lenses) is original prose written from general practitioner knowledge; the open-source pool informed the **shape** of measurement and the **methodological vocabulary** rather than supplying step lists.

## Confidence

**High** on the methodology — the four skills cover orthogonal, well-defined problems (operational audit, structured testing, measurement-program review, unit-economics math) with consistent vocabulary and explicit boundaries between them. They cross-reference each other in the "do not use this skill for" sections, which should keep the marketplace experience coherent.

**Medium-high** on the source coverage — the open-source pool for paid acquisition is thin compared to data/engineering niches. The available MIT/Apache repos cluster around measurement (MMM, CLV, geo experiments) and barely cover the in-platform tactical work (negative-keyword management, audience structure, creative production). I disclosed sub-threshold repos transparently and leaned on general practitioner knowledge for the platform-tactical parts of the audit and creative-test-planner skills. This is consistent with the brief's expectation that ad-platform repos are sparse and measurement/spreadsheet tooling should anchor the source list.

**High** on license diligence — every cited repo was license-verified via direct WebFetch. Two strong-fit candidates (Brainlabs scripts, Facebook capi-param-builder) were rejected outright on license grounds and excluded from the source lists despite their topical relevance.

## Tool-call budget

Roughly 11 web tool calls (4 WebSearch + 7 WebFetch), well under the 15-call ceiling specified in the brief. No tool-call thrash; one search → verify → discard cycle on each candidate repo.
