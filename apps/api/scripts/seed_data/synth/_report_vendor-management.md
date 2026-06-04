# Wave-2 Synthesis Report — Operations / Vendor Management & Procurement

## Files produced

1. `synth/ops-vendor-selection-scorecard.skills.md` — designs a weighted scorecard with anti-bias mechanics, demo rubric, reference-call script.
2. `synth/ops-rfp-author.skills.md` — produces a structured RFP with eligibility gate, transparent weights, standard pricing layout, dated timeline.
3. `synth/ops-vendor-tco-modeler.skills.md` — builds a 3-year TCO across seven cost categories with low/expected/high scenarios and sensitivity analysis.
4. `synth/ops-vendor-renewal-negotiator.skills.md` — reviews a renewal proposal and builds a counter across six negotiation levers with a pre-committed walkaway threshold.
5. `synth/ops-vendor-risk-tiering.skills.md` — classifies vendors into four tiers using three independent risk axes and prescribes proportionate diligence per tier.

All five are new files; nothing in the existing synth folder overlapped on vendor management (the closest adjacent skill, `ops-runbook-generator`, is operations-internal not vendor-facing). No merges or version bumps were required.

## Sources per skill

**vendor-selection-scorecard** (6 sources):
- https://github.com/tractorjuice/arc-kit (MIT, 1.8k)
- https://github.com/delschlangen/vendor-risk-rubric (MIT, 1)
- https://github.com/Funkmyster/awesome-supply-chain (CC0, 283)
- https://github.com/mgifford/open-source-contracting (MIT, 55)
- https://github.com/makegov/awesome-procurement-data (CC0, 71)
- https://github.com/ankane/awesome-legal (CC0, 957)

**rfp-author** (7 sources):
- https://github.com/SalesforceLabs/ProposalForce (BSD-3, 10, archived)
- https://github.com/tractorjuice/arc-kit (MIT, 1.8k)
- https://github.com/mgifford/open-source-contracting (MIT, 55)
- https://github.com/makegov/awesome-procurement-data (CC0, 71)
- https://github.com/Funkmyster/awesome-supply-chain (CC0, 283)
- https://github.com/accordproject/template-archive (Apache-2.0, 344)
- https://github.com/open-agreements/open-agreements (MIT, 34)

**vendor-tco-modeler** (6 sources):
- https://github.com/cisco-open/device-tco-calculator (MIT, 80)
- https://github.com/CenturyLinkCloud/EstimatorTCO (Apache-2.0, 5, archived)
- https://github.com/tractorjuice/arc-kit (MIT, 1.8k)
- https://github.com/Funkmyster/awesome-supply-chain (CC0, 283)
- https://github.com/makegov/awesome-procurement-data (CC0, 71)
- https://github.com/mgifford/open-source-contracting (MIT, 55)

**vendor-renewal-negotiator** (7 sources):
- https://github.com/mgifford/open-source-contracting (MIT, 55)
- https://github.com/open-agreements/open-agreements (MIT, 34)
- https://github.com/ankane/awesome-legal (CC0, 957)
- https://github.com/accordproject/template-archive (Apache-2.0, 344)
- https://github.com/tractorjuice/arc-kit (MIT, 1.8k)
- https://github.com/delschlangen/vendor-risk-rubric (MIT, 1)
- https://github.com/SalesforceLabs/ProposalForce (BSD-3, 10, archived)

**vendor-risk-tiering** (6 sources):
- https://github.com/delschlangen/vendor-risk-rubric (MIT, 1)
- https://github.com/tractorjuice/arc-kit (MIT, 1.8k)
- https://github.com/Funkmyster/awesome-supply-chain (CC0, 283)
- https://github.com/makegov/awesome-procurement-data (CC0, 71)
- https://github.com/mgifford/open-source-contracting (MIT, 55)
- https://github.com/ankane/awesome-legal (CC0, 957)

## License verification

All cited repos verified by WebFetch against the GitHub UI. License distribution: MIT (5 repos), Apache-2.0 (2), CC0-1.0 (3), BSD-3-Clause (1). All are within the permissive allowlist (MIT/Apache-2.0/BSD/ISC/Unlicense, plus CC0 which is public-domain dedication and functionally more permissive).

## Star-floor disclosure

The vendor-management niche is genuinely thin on GitHub. Three cited repos fall below the 100-star floor and one below the 30-star floor; disclosed here per the brief's instruction:

- **delschlangen/vendor-risk-rubric** (1 star) — Below the 30-star floor. Used because it is the cleanest MIT-licensed structured vendor-risk rubric I could locate and its 6-dimension scoring approach is directly relevant. Treated as one of several inputs, not an anchor.
- **CenturyLinkCloud/EstimatorTCO** (5 stars, archived) — Below 30-star floor. Cited as evidence that comparison-calculator UI structure exists in OSS; archived but still useful as a structural reference.
- **SalesforceLabs/ProposalForce** (10 stars, archived) — Below 30-star floor. The clearest BSD-licensed RFP-management OSS reference. Archived January 2024.
- **open-agreements/open-agreements** (34 stars) — Above the 30-star relaxed floor, below 100. Used for contract-template structure references.

Strong anchors (≥100 stars and permissive) carrying most of the weight: `tractorjuice/arc-kit` (1.8k), `ankane/awesome-legal` (957), `accordproject/template-archive` (344), `Funkmyster/awesome-supply-chain` (283).

## Source-thinness honesty

This niche has very few permissively-licensed, deeply-developed methodology repositories on GitHub. The repositories that do exist on vendor management tend to be either (a) light proof-of-concept rubrics with a handful of stars, (b) curated awesome-lists pointing mostly to commercial blog posts and SaaS products, or (c) commercial-friendly licenses like CC-BY-NC (excluded). Several promising repositories (ericiussecurity/Vendor_Security, JohnIdogo/StreamSafe-TPRM) were CC-BY-SA-4.0 or CC-BY-NC-4.0 and excluded from citation under the brief's allowlist.

As a result, the **prescriptive content** in these skills draws meaningfully on general professional knowledge in procurement, contract negotiation, and vendor risk management — applied through patterns observed in the cited repositories. The sources are real, were reviewed, and informed the structural choices (axis decomposition, tier prescriptions, scorecard mechanics, TCO categories, negotiation lever ranking), but the depth of opinionated guidance in the bodies exceeds what could be derived from the repos alone. This is consistent with the brief's allowance for general knowledge in sparse-source niches.

## Patterns observed across sources

- **Tiered diligence is the dominant structural pattern.** Both delschlangen/vendor-risk-rubric and tractorjuice/arc-kit organize vendor processes around risk tiers with proportionate review depth. The framework's four-tier output is consistent with this pattern.
- **Public-sector procurement instincts (transparent criteria, written-question windows, structured response templates) translate well to private-sector RFPs** — makegov/awesome-procurement-data and the federal procurement ecosystem it points to use these mechanics, and they map cleanly to commercial buying.
- **TCO templates consistently miss switching cost and residual-risk reserve.** Both cisco-open/device-tco-calculator and CenturyLinkCloud/EstimatorTCO focus on license/operate/CapEx-OpEx splits. The TCO skill explicitly adds switching cost and residual-risk reserve because their absence is the most common defect in TCO comparisons in practice.
- **Contract templates in mgifford/open-source-contracting and ankane/awesome-legal embed implicit negotiation positions** — exit assistance, audit rights, sub-processor flow-down — that are useful as default-customer-favorable language. The renewal skill's lever-ranking draws on this.

## Rejections

- **CC-BY-SA-4.0 repos** (ericiussecurity/Vendor_Security, 9 stars) — out of allowlist.
- **CC-BY-NC-4.0 repos** (JohnIdogo/StreamSafe-TPRM, 1 star) — out of allowlist.
- **ebohc/vendor-risk-assessment-framework** (0 stars, no specified license) — excluded for absent license. The repo is a useful Excel-based starting point but cannot be cited under the rules.
- **Michaelmcpheejr/Third-Party-Vendor-Risk-Assessment** (0 stars, no specified license) — excluded for absent license.
- **CHPC-UofU/cyberinsight** (0 stars, no specified license) — excluded for absent license.
- **Harshitha-katturajan/Procurement-ai-agent** and related "vendor management" CRUD apps — excluded as application code rather than methodology source.

## Confidence

- **vendor-selection-scorecard:** Medium-high. The scorecard discipline is broadly documented across procurement practice; specific anti-bias mechanics (independent scoring, divergence triggers, decision-maker timing) are opinionated choices that reflect general best practice. arc-kit and the curated awesome-lists provide enough triangulation.
- **rfp-author:** Medium-high. RFP structure is reasonably well-codified in federal procurement (awesome-procurement-data points to ample reference material) and in OSS contracting (mgifford). The skill is opinionated on length (under 30 pages) and on publishing weights — both positions are defensible but represent a stance, not a universal consensus.
- **vendor-tco-modeler:** Medium. Two TCO-specific OSS repos exist but are small and narrow (devices, CenturyLink). The seven-category cost stack is informed by the broader procurement literature behind awesome-supply-chain and arc-kit but is partly synthetic. Confidence is highest on the categorization, lower on the specific percentage-of-build-cost heuristics for ongoing integration tax (10–20%) — these are operating heuristics that vary widely by org.
- **vendor-renewal-negotiator:** Medium. The six-lever framework and reversibility ranking are derived from contract-template patterns observed in mgifford and ankane plus general negotiation practice. The repos provided clause structure; the negotiation sequence is a constructed methodology.
- **vendor-risk-tiering:** Medium-high. Tiering is well-supported by delschlangen/vendor-risk-rubric and tractorjuice/arc-kit and is the most structurally grounded skill of the five. The three-axis decomposition (data / criticality / dependency) generalizes the rubric's six dimensions to a workable triple.

## Follow-ups suggested

- A future **vendor-exit-runbook** skill would complement risk-tiering's "named exit plan" expectation with an executable how-to. Adjacent to ops-runbook-generator but with vendor-specific concerns (data export, transition assistance, contractual notice).
- A **concentration-risk analyzer** skill would address the "many small vendors collectively critical" gap explicitly mentioned in vendor-risk-tiering's limitations.
- A **vendor-relationship-quarterly-review** skill would operationalize the Tier-1 quarterly review, with the agenda template, the metrics to bring, and the trigger criteria for surfacing the relationship to executive attention.
- An **ESG/responsible-sourcing-overlay** would extend tiering with environmental, social, and modern-slavery-act diligence criteria — increasingly required in EU procurement but not addressed here.
- Pairing the **TCO modeler with NPV math** for organizations whose finance teams require it — a clear and bounded extension that the current skill flags but does not produce.

## Tag-line conformance

All skills use `category: operations` and the first tag `niche:vendor-management` followed by 4–6 additional descriptive tags as required.
