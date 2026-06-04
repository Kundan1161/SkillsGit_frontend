# Synthesis Report — Engineering / Code Review & PR Auditing

**Date:** 2026-05-14
**Author:** methodology-synthesis agent
**Area:** engineering — code review, PR auditing, security review, refactor spotting

## Skills produced

1. `eng-code-review-auditor.skills.md` — PR Review Auto-Auditor ($99 one-time)
2. `eng-security-code-review.skills.md` — Security Code Review Pass ($11/mo subscription)
3. `eng-refactor-spotter.skills.md` — Refactor Opportunity Spotter ($9/mo subscription)

All three skills exceed 300 body lines of original instructional prose and cite ≥7 permissively-licensed sources each.

## Sources reviewed

All sources verified as permissively licensed (MIT, Apache-2.0, BSD-2/3-Clause, ISC, or Unlicense), ≥100 stars, and active within the last 18 months. URLs only — no quoted content from any source appears in the produced skills.

### Accepted (used as sources across the three skills)

| Repo | License | Stars | Last push | Used by |
| --- | --- | --- | --- | --- |
| `reviewdog/reviewdog` | MIT | 9.3k | 2026-05 | all three |
| `Nayjest/Gito` | MIT | 233 | 2026-04 | all three |
| `codedog-ai/codedog` | MIT | 196 | 2026-04 | auditor, refactor |
| `anc95/ChatGPT-CodeReview` | ISC | 4.4k | 2026-02 | auditor, refactor |
| `Nikita-Filonov/ai-review` | Apache-2.0 | 426 | 2026-05 | all three |
| `eslint/eslint` | MIT | 27.3k | 2026-05 | auditor, refactor |
| `analysis-tools-dev/static-analysis` | MIT | 14.5k | 2026-05 | all three |
| `Luzkan/smells` | MIT | 276 | 2026-05 | auditor, refactor |
| `PyCQA/bandit` | Apache-2.0 | 8.0k | 2026-05 | security |
| `securego/gosec` | Apache-2.0 | 8.8k | 2026-05 | security |
| `gitleaks/gitleaks` | MIT | 27.0k | 2026-05 | security |
| `awslabs/git-secrets` | Apache-2.0 | 13.3k | 2025-09 | security |
| `zaproxy/zaproxy` | Apache-2.0 | 15.1k | 2026-05 | security |

### Rejected (and why)

| Repo | Reason |
| --- | --- |
| `Bearer/bearer` | `NOASSERTION` license — cannot confirm permissive. |
| `OWASP/www-project-code-review-guide` | `CC-BY-SA-4.0` (not in allowed list) and archived (last push 2022). |
| `joho/awesome-code-review` | No license declared — cannot use. |
| `softwaresecured/secure-code-review-checklist` | No license; last push 2018 — dormant. |
| `semgrep/semgrep` | `LGPL-2.1` — disallowed. |
| `qodo-ai/pr-agent` | `AGPL-3.0` — disallowed. |
| `trailofbits/semgrep-rules` | `AGPL-3.0` — disallowed. |
| `Codium-ai/cover-agent` | `AGPL-3.0` — disallowed. |
| `google/eng-practices` | `NOASSERTION` — cannot confirm permissive. |
| `thoughtbot/guides` | No license declared. |
| `mawrkus/pull-request-review-guide` | No license + dormant since 2024-10. |
| `golangci/golangci-lint` | `GPL-3.0` — disallowed. |
| `sonarsource/sonarqube` | `LGPL-3.0` — disallowed. |

## Methodology patterns identified across sources

These patterns recurred across multiple permissively-licensed sources and shaped the structure of the produced skills. None of the text is borrowed; the abstractions are.

1. **Diff-anchored review with line precision.** Most automated review tools surveyed (reviewdog, Gito, ChatGPT-CodeReview, ai-review, codedog) anchor findings to specific files and line ranges in the diff. This pattern is the backbone of the auditor skill.
2. **Severity tiers with a "filter by importance" affordance.** gosec, bandit, eslint, and reviewdog all converge on three-to-four severity levels (info/low/warn → medium → error/high → critical). The skills standardize on Blocker / Major / Minor / Nit for the auditor; Critical / High / Medium / Low / Informational for security; High / Medium / Low payoff for refactor.
3. **Category-driven sweeps rather than ad-hoc reasoning.** bandit's B-codes, gosec's G-categories, the ESLint rule namespaces, and the code-smells catalog all reflect that "walking a checklist" produces more consistent results than "reading freely." The skills adopt explicit category sweeps.
4. **Trust boundary identification before sink analysis.** Bandit, gosec, and the OWASP-shaped tools all assume a taint-style mental model: identify sources, identify sinks, trace paths. The security skill makes this an explicit Stage 1.
5. **Configurable suppression.** gitleaks' allowlists, eslint's per-rule disable comments, reviewdog's filtering modes — all reflect that real-world adoption requires the tool to defer to the team's stated framework protections. The security skill takes `framework_protections` as an input and respects it.
6. **Reporting hygiene — capping noise.** Several tools (codedog, ai-review, ChatGPT-CodeReview) discuss caps on the number of findings or summarization modes to keep reports readable. The skills cap nits at 8 and Informational findings at 6.
7. **Multi-mode review.** ai-review's inline / context / summary modes inspired the auditor's "report grouped by severity, plus machine-readable JSON for posting" dual output. The same pattern shows up in PR-agent-style tools.
8. **CI/CD integration as default invocation pattern.** Across tools the trigger is the PR event; the workflow is automatic. The skills are designed for that invocation pattern (one-shot, with all needed inputs supplied by the caller) but also support manual invocation by a developer at a CLI.
9. **The smell catalog model.** Luzkan/smells encodes ~50 distinct code smells with stable names. The refactor skill adopts the smell-name → refactor-move mapping discipline rather than free-form prose.

## Pricing rationale

- **PR Review Auto-Auditor at $99 one-time.** This is a flagship reference skill; one-time pricing matches the task spec recommendation and the depth of the methodology justifies a higher anchor.
- **Security Code Review Pass at $11/mo subscription with support.** Security best practices and the CWE/OWASP shapes evolve quickly; subscribers get ongoing updates and support, matching the task spec.
- **Refactor Opportunity Spotter at $9/mo subscription.** Lower price reflects narrower utility (refactor work is occasional in many teams) and the subscription matches catalog updates as new refactoring moves enter common practice.

All three sit inside the $5–$11 subscription band and $99 one-time anchor specified by the task.

## Decisions made under ambiguity

- **The OWASP CC-BY-SA-4.0 license is not in the allowed list.** I could have used it under fair-use reasoning, but the task is explicit: only MIT/Apache/BSD/ISC/Unlicense. I sourced OWASP-shaped methodology from secondary tools (bandit, gosec, zaproxy) that are permissively licensed and reflect the same standards.
- **Bearer is borderline.** Its public README references "permissive" but the GitHub API returned `NOASSERTION`. I excluded it rather than guess.
- **Eslint and Luzkan/smells contributed methodology to both the auditor and refactor skills.** Both skills cite them; this is appropriate because the underlying patterns (rule organization, smell taxonomy) genuinely inform both methodologies.
- **PR-agent / qodo-merge** would have been the most natural primary source for the auditor skill, but it's AGPL-3.0 and disallowed. The auditor's methodology was instead synthesized from reviewdog, Gito, codedog, ai-review, and ChatGPT-CodeReview.
- **No GPL or LGPL repos were read.** I confirmed the license tab on every candidate before doing methodology extraction. semgrep, semgrep-rules, sonarqube, golangci-lint, and pr-agent were all license-rejected before any deep dive.

## Originality discipline

- All prose in the three skill files was written from scratch. The agent did not paste or paraphrase verbatim from any source.
- For each source the agent extracted *concepts* (categories tracked, severity levels used, workflow stages) and re-expressed them in the agent's own framing.
- The smell catalog in the refactor skill uses canonical refactoring-move names (Extract Method, Replace Magic Number With Named Constant, etc.) that are common-vocabulary in the field; these names are not specific to any cited repo and predate them by decades.
- No trademarked methodology names were used. Tool brand names (e.g., "reviewdog", "bandit") appear only in the `## Sources reviewed` URLs.

## Confidence assessment

- **PR Review Auto-Auditor — High.** Strong source diversity (5+ LLM-review tools, ESLint as a reference for severity, the smells catalog for naming), the methodology is well-trodden, and the skill maps closely to how senior reviewers actually work. The $99 price point is defensible.
- **Security Code Review Pass — High.** OWASP-shaped categories are widely understood; bandit/gosec/gitleaks/zaproxy provided concrete evidence of how production tools structure their findings. The skill's stance on suppression, exploitation sketches, and severity combos is the part most likely to need tuning post-publish.
- **Refactor Opportunity Spotter — Medium.** Confident on the smell catalog and the refactor-move vocabulary. Less confident on the "ambitious scope" architectural moves — those are inherently context-dependent and the skill leans on the user to supply `codebase_style`. The $9/mo price reflects the narrower applicability.

## Open follow-ups (not blocking)

- The security skill's "language and framework specifics" stage is broad but shallow on each framework. A v1.1 could split into per-framework variants (Django-specific, Spring-specific) if buyer feedback warrants.
- The auditor's "AI-generated diff" stage is necessarily speculative as model behavior evolves; consider re-tuning quarterly.
- The refactor skill could grow a companion skill for "characterization-test author" that emits the tests needed before a risky refactor — currently it just recommends adding them.
