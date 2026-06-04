---
id: skillsgit-curated/imported-google-skills-waf-security
version: 1.0.0
name: Google Cloud Well-Architected — Security
description: Apply the Google Cloud Well-Architected Framework Security pillar — security-by-design, zero trust, shift-left, preemptive cyber defense, AI security, and compliance.
authors:
  - name: Google (original)
    handle: google
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-google, gcp, well-architected, security, zero-trust, compliance]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gemini-2.0-pro]
trigger_keywords: [waf security, zero trust, shift left, security command center, vpc service controls, ai security]
example_invocations:
  - "Audit a workload against the WAF security pillar."
  - "Recommend zero-trust controls for a new internal app."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from google/skills under Apache-2.0.
---

# Google Cloud Well-Architected Framework — Security pillar

## When to use

Use this skill to evaluate a workload, identify security requirements, and provide actionable recommendations for IAM, network security, data protection, and operational security under the Google Cloud Well-Architected Framework Security pillar.

## How to apply

Anchor on the seven security principles. Use the workload assessment questions in the matching subsection (security-by-design, zero trust, shift-left, preemptive cyber defense, AI security, AI-for-security, compliance and privacy) to elicit the workload's current posture. Then walk the validation checklist to score alignment.

## Overview

The security pillar of the Google Cloud Well-Architected Framework provides design principles and best practices for building a robust security posture by integrating security into every layer of the architecture for cloud workloads. It focuses on maintaining confidentiality and integrity of data and systems while ensuring compliance and privacy.

## Core principles

- Implement security by design: https://docs.cloud.google.com/architecture/framework/security/implement-security-by-design
- Implement zero trust: https://docs.cloud.google.com/architecture/framework/security/implement-zero-trust
- Implement shift-left security: https://docs.cloud.google.com/architecture/framework/security/implement-shift-left-security
- Implement preemptive cyber defense: https://docs.cloud.google.com/architecture/framework/security/implement-preemptive-cyber-defense
- Use AI securely and responsibly: https://docs.cloud.google.com/architecture/framework/security/use-ai-securely-and-responsibly
- Use AI for security: https://docs.cloud.google.com/architecture/framework/security/use-ai-for-security
- Meet regulatory, compliance, and privacy needs: https://docs.cloud.google.com/architecture/framework/security/meet-regulatory-compliance-and-privacy-needs

## Relevant Google Cloud products

- Identity and access management: IAM, Identity-Aware Proxy (IAP), Chrome Enterprise Premium.
- Network security: Google Cloud Armor, VPC Service Controls, Cloud NGFW, Shared VPC, Cloud Interconnect and IPsec VPN.
- Data security: Cloud KMS, Sensitive Data Protection (formerly Cloud DLP), Confidential Computing.
- Security operations: Google SecOps (Chronicle), Security Command Center, Cloud Logging and Cloud Monitoring.
- Automation and supply chain: Cloud Build, Artifact Analysis, Binary Authorization, Assured Open Source Software.

## Workload assessment questions

Ask questions from each principle's subsection to understand the workload's posture. Subsections cover: security-by-design, zero trust, shift-left, preemptive cyber defense, AI workload security, AI for security, and regulatory compliance and privacy. Sample questions:

- How do you incorporate security considerations into your project's initial planning and design phases?
- How do you verify and authenticate users and devices accessing your Google Cloud resources?
- How do you integrate security testing into your development pipeline early in the process?
- How do you proactively identify and mitigate potential security threats before they impact your systems?
- How do you ensure the security of your AI models and data?
- How do you leverage AI and ML to enhance your security posture?
- What regulatory compliance frameworks and privacy standards do you need to adhere to?

## Validation checklist

### Security by design
- Are system components selected based on their security features and hardening?
- Is defense-in-depth implemented at the network, host, and application layers?
- Are safe libraries and application frameworks used to prevent common vulnerabilities?
- Is a risk assessment performed using industry standards?

### Zero trust
- Is access control enforced based on user identity and context (device, location)?
- Are private connectivity methods (Cloud Interconnect, VPN) used for internal traffic?
- Are default networks disabled in all projects?
- Are VPC Service Controls perimeters established around sensitive data?

### Shift-left security
- Is infrastructure provisioned using Infrastructure as Code (e.g., Terraform)?
- Are automated security scans integrated into the CI/CD pipeline?
- Is there a process for scanning and patching vulnerabilities in dependencies?
- Is Binary Authorization used to ensure only trusted images are deployed?

### Preemptive cyber defense
- Is threat intelligence integrated into security operations?
- Is security logging enabled and centralized for all critical resources?
- Are automated responses configured for common security threats?
- Are defenses validated through periodic testing or red-teaming?

### AI security and governance
- Are AI pipelines secured against tampering and data poisoning?
- Is differential privacy or data masking used for training data where appropriate?
- Are Vertex Explainable AI and fairness indicators used for model governance?

## Attribution

This skill was imported from `google/skills` under the Apache-2.0 license. Original content authored by Google. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections; addition of `## When to use` and `## How to apply` stubs required by our validator. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed

- https://github.com/google/skills/tree/main/skills/cloud/google-cloud-waf-security (Apache-2.0)
