/**
 * Phase 0 template descriptors. Real templates ship with a starter
 * graph payload in Phase 3 (see `skill-creator/01-visual-builder.md`).
 *
 * For now this is just the metadata used to render `/templates`.
 */

export type TemplateCategory =
  | "finance"
  | "design"
  | "marketing"
  | "engineering"
  | "operations"
  | "legal"
  | "sales"
  | "support";

export interface TemplateDescriptor {
  id: string;
  name: string;
  category: TemplateCategory;
  description: string;
}

export const TEMPLATES: TemplateDescriptor[] = [
  {
    id: "finance-dcf",
    name: "DCF Valuation",
    category: "finance",
    description:
      "Walk a 10-K through assumptions, projections, and a discounted cash flow.",
  },
  {
    id: "finance-monthly-close",
    name: "Monthly Close Checklist",
    category: "finance",
    description:
      "Step the agent through accruals, reconciliations, and variance commentary.",
  },
  {
    id: "finance-budget-variance",
    name: "Budget Variance Analyzer",
    category: "finance",
    description:
      "Decompose actuals vs. budget into price, volume, and mix drivers.",
  },

  {
    id: "design-critique",
    name: "Design Critique Rubric",
    category: "design",
    description:
      "Score a screen on hierarchy, accessibility, brand fit, and ship-readiness.",
  },
  {
    id: "design-accessibility-audit",
    name: "Accessibility Audit",
    category: "design",
    description:
      "Walk an interface against WCAG 2.2 AA checks and produce a prioritized fix list.",
  },
  {
    id: "design-brand-review",
    name: "Brand Voice Review",
    category: "design",
    description: "Compare copy and visuals against an uploaded brand guide.",
  },

  {
    id: "marketing-campaign-brief",
    name: "Campaign Brief Builder",
    category: "marketing",
    description:
      "Turn a goal + audience into a positioning, channel mix, and content calendar.",
  },
  {
    id: "marketing-seo-audit",
    name: "SEO Audit",
    category: "marketing",
    description:
      "Crawl a page, score on-page signals, flag content gaps versus competitors.",
  },
  {
    id: "marketing-email-sequence",
    name: "Email Sequence Designer",
    category: "marketing",
    description:
      "Design a multi-email nurture flow with timing, branching, and exit criteria.",
  },

  {
    id: "engineering-pr-review",
    name: "Pull Request Review",
    category: "engineering",
    description:
      "Review a diff for security, performance, and correctness with prioritized comments.",
  },
  {
    id: "engineering-incident-postmortem",
    name: "Incident Postmortem",
    category: "engineering",
    description:
      "Structure a blameless postmortem from timeline, impact, and contributing factors.",
  },
  {
    id: "operations-vendor-review",
    name: "Vendor Review",
    category: "operations",
    description:
      "Build a TCO breakdown, risk profile, and renew/replace recommendation.",
  },
  {
    id: "legal-nda-triage",
    name: "NDA Triage",
    category: "legal",
    description:
      "Classify a counterparty NDA as green / yellow / red against your playbook.",
  },
  {
    id: "sales-call-prep",
    name: "Sales Call Prep",
    category: "sales",
    description:
      "Research an account and attendees, propose an agenda, surface objections.",
  },
  {
    id: "support-ticket-triage",
    name: "Support Ticket Triage",
    category: "support",
    description:
      "Categorize an inbound ticket, set priority, route to the right queue.",
  },
];

export function templatesByCategory(): Record<
  TemplateCategory,
  TemplateDescriptor[]
> {
  const out = {} as Record<TemplateCategory, TemplateDescriptor[]>;
  for (const t of TEMPLATES) {
    if (!out[t.category]) out[t.category] = [];
    out[t.category]!.push(t);
  }
  return out;
}
