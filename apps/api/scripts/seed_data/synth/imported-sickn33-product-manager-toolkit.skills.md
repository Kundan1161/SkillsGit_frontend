---
id: skillsgit-curated/imported-sickn33-product-manager-toolkit
version: 1.0.0
name: Product Manager Toolkit
description: Essential frameworks for modern product management from discovery to delivery, including RICE prioritization, customer interview analysis, and PRD templates.
authors:
  - name: sickn33 community
    handle: sickn33
    role: author
  - name: skillsgit-curated
    handle: skillsgit-curated
    role: maintainer
category: productivity
tags: [imported, source-sickn33, product-management, rice, prd, discovery]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from sickn33/antigravity-awesome-skills under MIT (code) / CC BY 4.0 (content).
---

# Product Manager Toolkit

Essential tools and frameworks for modern product management, from discovery to delivery.

## When to use

- Prioritizing a feature backlog with RICE scoring
- Synthesizing insights from a batch of customer interviews
- Drafting a PRD for a feature heading into design or build
- Planning a quarterly roadmap against fixed team capacity

## How to apply

### Feature Prioritization Process

1. **Gather Feature Requests** - customer feedback, sales requests, technical debt, strategic initiatives
2. **Score with RICE** - Reach (users/quarter), Impact (massive/high/medium/low/minimal), Confidence (high/medium/low), Effort (person-months)
3. **Analyze Portfolio** - quick wins vs big bets, effort distribution, strategy alignment
4. **Generate Roadmap** - quarterly capacity, dependency mapping, stakeholder alignment

### Customer Discovery Process

1. **Conduct Interviews** - semi-structured format, focus on problems not solutions
2. **Analyze Insights** - pain points with severity, feature requests with priority, jobs-to-be-done, sentiment, themes
3. **Synthesize Findings** - group similar pain points, identify patterns, map to opportunity areas
4. **Validate Solutions** - hypothesis statements, prototype tests, measure actual vs expected behavior

### PRD Development Process

1. **Choose Template** based on scope:
   - **Standard PRD**: complex features (6-8 weeks)
   - **One-Page PRD**: simple features (2-4 weeks)
   - **Feature Brief**: exploration phase (~1 week)
   - **Agile Epic**: sprint-based delivery
2. **Structure Content**: Problem -> Solution -> Success Metrics; always include out-of-scope; clear acceptance criteria
3. **Collaborate**: engineering (feasibility), design (experience), sales (market validation), support (operational impact)

## Prioritization Frameworks

### RICE
```
Score = (Reach x Impact x Confidence) / Effort

Impact:     Massive=3, High=2, Medium=1, Low=0.5, Minimal=0.25
Confidence: High=100%, Medium=80%, Low=50%
Effort:     person-months
```

### Value vs Effort Matrix
```
         Low Effort       High Effort
High     QUICK WINS       BIG BETS
Value    [Prioritize]     [Strategic]
Low      FILL-INS         TIME SINKS
Value    [Maybe]          [Avoid]
```

### MoSCoW
- **Must Have**: Critical for launch
- **Should Have**: Important but not critical
- **Could Have**: Nice to have
- **Won't Have**: Out of scope

## Discovery Frameworks

### Customer Interview Guide

- **Context** (5 min): role, responsibilities, current workflow, tools used
- **Problem Exploration** (15 min): pain points, frequency, impact, workarounds
- **Solution Validation** (10 min): reaction to concepts, value perception, willingness to pay
- **Wrap-up** (5 min): other thoughts, referrals, follow-up permission

### Hypothesis Template
```
We believe that [building this feature]
For [these users]
Will [achieve this outcome]
We'll know we're right when [metric]
```

### Opportunity Solution Tree
```
Outcome
├── Opportunity 1
│   ├── Solution A
│   └── Solution B
└── Opportunity 2
    └── Solution C
```

## Metrics & Analytics

### North Star Metric
1. Identify core value
2. Make it measurable
3. Ensure it's actionable
4. Check it's a leading indicator of business success

### Funnel Analysis
Acquisition -> Activation -> Retention -> Revenue -> Referral. Track conversion rate, drop-off points, time between steps, cohort variations.

### Feature Success Metrics
- **Adoption**: % of users using feature
- **Frequency**: usage per user per period
- **Depth**: % of feature capability used
- **Retention**: continued usage over time
- **Satisfaction**: NPS/CSAT for the feature

## Best Practices

**Great PRDs**: Start with the problem; include success metrics upfront; explicitly state out-of-scope; use visuals; keep technical details in appendix; version control changes.

**Effective Prioritization**: Mix quick wins with strategic bets; consider opportunity cost; account for dependencies; buffer ~20% for unexpected work; revisit quarterly; communicate decisions.

**Customer Discovery**: Ask "why" five times; focus on past behavior, not future intentions; avoid leading questions; interview in their environment; look for emotional reactions; validate with data.

**Stakeholder Management**: Identify RACI for decisions; regular async updates; demo over documentation; address concerns early.

## Common Pitfalls

1. **Solution-First Thinking** - jumping to features before understanding problems
2. **Analysis Paralysis** - over-researching without shipping
3. **Feature Factory** - shipping features without measuring impact
4. **Ignoring Technical Debt** - not allocating time for platform health
5. **Stakeholder Surprise** - not communicating early and often
6. **Metric Theater** - optimizing vanity metrics over real value

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Attribution

This skill was imported from `sickn33/antigravity-awesome-skills` under the MIT license (code) and CC BY 4.0 license (content/documentation). Original community author. Modifications by skillsgit: frontmatter normalization; removed inline references to specific python scripts that ship in the upstream repo; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/sickn33/antigravity-awesome-skills/tree/main/skills/product-manager-toolkit (MIT / CC BY 4.0)
