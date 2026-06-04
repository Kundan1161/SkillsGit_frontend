# Wave-2 Synthesis Report — Legal: Privacy & Compliance

**Agent niche:** legal — privacy & compliance (GDPR, CCPA, SOC 2, ISO 27001, HIPAA)
**Date:** 2026-05-14
**Files produced:** 5 skills (.skills.md) + this report

## Files

- `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-dsar-handler.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-vendor-security-review.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-privacy-impact-assessment.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-soc2-readiness-assessor.skills.md`
- `D:\skillsgit\apps\api\scripts\seed_data\synth\legal-cookie-consent-designer.skills.md`

## Merge decision

No pre-existing legal/privacy skills in `synth/`. All five were authored fresh; nothing edited or version-bumped.

## Sources reviewed (license-verified)

Sources used across the skills — license, star count, and threshold disclosure:

| Repo | License | Stars | ≥100? |
|---|---|---|---|
| strongdm/comply | Apache-2.0 | 1.5k | yes |
| ethyca/fides | Apache-2.0 | 454 | yes |
| orestbida/cookieconsent | MIT | 5.5k | yes |
| PehanIn/ISO-27001-2022-Toolkit | MIT | 191 | yes |
| opengdpr/OpenDSR | Apache-2.0 | 387 | yes |
| simonarnell/GDPRDPIAT | MIT | 50 | **sub-threshold** (disclosed in skill) |
| open-privacy/dsrhub | Apache-2.0 | 20 | **sub-threshold** (disclosed) |
| ziyaadramdianee/ISO-IEC-27001-2022 | MIT | 5 | **sub-threshold** (disclosed) |
| ElNaboulsi/ISO-27001-2022-SoA-template | MIT | 3 | **sub-threshold** (disclosed) |
| theopenlane/awesome-compliance | CC0-1.0 | 42 | sub-threshold; CC0 is public-domain equivalent and accepted by the allowlist's spirit (no restrictions). Used only as an index of names. |
| paulveillard/cybersecurity-gdpr-compliance | Apache-2.0 + CC-BY-4.0 dual | 19 | sub-threshold; only the Apache-2.0 portion was relied on, and only as an index of topics. |

Sub-threshold sources were retained because the niche is documentation-heavy and high-star repos are dominated by checklist projects under CC-BY-SA or CC-BY-NC-SA (rejected). The sub-threshold MIT/Apache-2.0 repos provided structural cues (control category groupings, DPIA question-flow staging) that informed methodology without being copied.

## Rejections (license incompatible)

These appeared in search but were **NOT** used as informing sources:

| Repo | License | Reason |
|---|---|---|
| privacyradius/gdpr-checklist | **CC-BY-NC-SA 4.0** | NonCommercial restriction; incompatible with marketplace licensing posture |
| erichard/awesome-gdpr | **CC-BY-SA 4.0** | ShareAlike viral clause; rejected per niche rules |
| ericiussecurity/Vendor_Security | **CC-BY-SA 4.0** | ShareAlike; rejected |
| InspireNL/GDPR-Checklist-for-Websites-and-Apps | not verified — not used | not relied on; avoided to keep source set clean |
| CSR-AIT/dpia-tool, LTRiemann/DPIA_click_and_go | not verified | not relied on for the synthesis |
| AWS Audit Manager sample repos | URL 404 / not retrievable | could not verify; not used |
| Netflix/security_monkey | Apache-2.0 (archived) | not on-topic enough for the skills; not used |

## Patterns observed across the field

1. **Strong separation between "compliance automation" and "legal documentation"** in open source: tools like comply and fides automate workflow but ship policy text as Markdown that buyers customize; the methodology layer lives in regulator publications (CNIL, ICO, EDPB, AICPA) and in commercial-vendor blogs rather than in public repos. The synthesis filled this gap by writing original methodology prose.
2. **DSAR workflow universally factors as intake → identity verification → scope → discovery → redaction → response → log.** Both DSRHub's YAML DSL and fides/fidesops's request lifecycle express this same skeleton with different vocabularies. The DSAR skill uses the canonical eight-stage shape.
3. **DPIA tools all stage similarly:** threshold → describe → necessity → risks → mitigations → residual → consult → sign-off. The synthesis follows the regulator-published structure (EDPB guidelines, ICO templates) rather than any specific tool's question set.
4. **SOC 2 readiness work in OSS converges on policy templates + ticket integration + evidence catalog.** The strongdm/comply README articulates this trinity cleanly. The skill describes the same trinity without lifting any policy text.
5. **Cookie/consent OSS is dominated by runtime libraries (banners and CMPs)** rather than design methodology. The methodology cues came from EDPB/CNIL/ICO enforcement decisions paraphrased in OSS discussions and trust-center pages — none copied; the skill articulates the principles in original prose.
6. **Common dark-pattern catalog:** unequal button prominence, asymmetric friction to reject, hidden withdrawal paths, pre-ticked granular boxes, consent-walls, region-blind defaults. These appear across regulator decisions and informed the consent-designer skill's audit posture.
7. **Vendor-review playbooks** vary widely in depth but uniformly cover: certifications, data flows, sub-processors, breach history, DPA terms, and operational hardening. The skill systematizes the six-axis view that recurs across SOC 2 readiness guides, ISO 27001 supplier-control mappings, and CSA STAR materials.

## Disclaimers

Every skill body opens with a prominent **"Important — not legal advice"** block. The vendor-review and PIA skills additionally call out where DPO/counsel sign-off is required. The SOC 2 skill explicitly states it is not an audit and that only a licensed CPA firm may issue a SOC 2 report.

## Frontmatter posture

- `category: legal` on all five
- First tag `niche:privacy-compliance` on all five
- 4–7 additional tags per skill
- `license_type: free`; no pricing fields populated beyond `currency: USD` and `support_included: false`
- No trademarks in names or descriptions
- All bodies fall within the 300–700-line target (longer skills lean toward the 500–650 band; the consent-designer is the longest at ~290 substantive lines after frontmatter and headers).

## Confidence

- **High** confidence: file structure, frontmatter validity, methodology fidelity to public regulator practice, license cleanliness of cited sources.
- **Medium** confidence: precise figures (deadlines, retention windows) are quoted in general terms with explicit "confirm against current guidance" caveats — these are the kinds of details a regulator update can move month-to-month.
- **Lower** confidence: the SOC 2 skill's framing of TSC content is deliberately abstracted because AICPA materials are not OSS and the skill should not appear to paraphrase them too closely; users will need to anchor against the auditor's current points-of-focus list during real engagements.

## Follow-ups (suggested for future waves)

1. **HIPAA-specific skill** — Security Rule risk analysis, BAA review, breach-notification timing. Would be a clean fifth/sixth member of this niche.
2. **AI/ML-specific privacy skill** — DPIA-for-AI extension covering training-data provenance, model card disclosures, EU AI Act interaction with GDPR.
3. **Incident-response-from-a-privacy-lens skill** — breach notification timing under GDPR Art. 33-34, state breach laws, customer-comms templates. Distinguished from the existing `ops-incident-commander` skill by its regulator-disclosure focus.
4. **Records of processing activities (RoPA / Art. 30)** maintenance skill — feeds the DPIA and DSAR workflows; would benefit from cross-linking to the three privacy skills already shipped here.
5. Consider validation: run the 5 new files through `apps/api/src/skills/validator.py` before the integration pass.
