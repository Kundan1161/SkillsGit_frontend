// @skillsgit/skills-schema
// Zod schemas + TypeScript types for skills.md frontmatter.
// See: prompts/shared/skills-md-spec.md
//
// Hand-maintained mirror of the canonical Pydantic models in
// apps/api/src/skills/validator.py. Update both in lockstep — the
// repo-root `pnpm codegen` placeholder will eventually do this for us
// (see ADR-017).
//
// Wave 1 (this file): adds the 5 ADR-009 optional fields (kind, links,
// parent_occupation_id, neuron, vault_path). The pre-ADR-009 fields
// (id, version, name, description, ai, …) are scaffolded with the
// minimum surface needed to keep the Pydantic ↔ Zod contract aligned;
// further fidelity follows in later waves.

import { z } from "zod";

// ── Enums (mirrored from the Pydantic ones) ─────────────────────────

export const SkillKind = z.enum([
  "skill",
  "occupation",
  "persona",
  "memory_neuron",
]);
export type SkillKind = z.infer<typeof SkillKind>;

export const AuthorRole = z.enum(["author", "contributor", "maintainer"]);
export type AuthorRole = z.infer<typeof AuthorRole>;

export const LicenseType = z.enum([
  "free",
  "one_time",
  "subscription",
  "freemium",
]);
export type LicenseType = z.infer<typeof LicenseType>;

export const InputType = z.enum([
  "text",
  "file",
  "url",
  "json",
  "number",
  "choice",
]);
export type InputType = z.infer<typeof InputType>;

export const OutputType = z.enum(["text", "markdown", "json", "file"]);
export type OutputType = z.infer<typeof OutputType>;

export const LinkRelation = z.enum([
  "applies",
  "extends",
  "contradicts",
  "see-also",
  "recorded-instance-of",
]);
export type LinkRelation = z.infer<typeof LinkRelation>;

// ── Sub-models ──────────────────────────────────────────────────────

export const Author = z.object({
  name: z.string(),
  handle: z.string().nullish(),
  role: AuthorRole.default("author"),
});
export type Author = z.infer<typeof Author>;

export const Pricing = z.object({
  one_time_cents: z.number().int().positive().nullish(),
  subscription_cents: z.number().int().positive().nullish(),
  currency: z
    .string()
    .length(3)
    .regex(/^[A-Z]{3}$/)
    .default("USD"),
  support_included: z.boolean().default(false),
});
export type Pricing = z.infer<typeof Pricing>;

export const AiBlock = z.object({
  required_models: z.array(z.string()).min(1),
  compatible_models: z.array(z.string()).default([]),
  min_context_tokens: z.number().int().positive().nullish(),
  tools_required: z.array(z.string()).default([]),
  tools_optional: z.array(z.string()).default([]),
  estimated_tokens_per_invocation: z.number().int().positive().nullish(),
});
export type AiBlock = z.infer<typeof AiBlock>;

export const SkillInput = z.object({
  name: z.string(),
  type: InputType,
  required: z.boolean().default(false),
  description: z.string().default(""),
  choices: z.array(z.string()).nullish(),
});
export type SkillInput = z.infer<typeof SkillInput>;

export const SkillOutput = z.object({
  name: z.string(),
  type: OutputType,
  description: z.string().default(""),
});
export type SkillOutput = z.infer<typeof SkillOutput>;

export const ChangelogEntry = z.object({
  version: z.string(),
  date: z.string(), // ISO date string
  notes: z.string().default(""),
  breaking: z.boolean().default(false),
});
export type ChangelogEntry = z.infer<typeof ChangelogEntry>;

export const Distribution = z
  .object({
    content_hash: z.string().nullish(),
    signed_at: z.string().nullish(),
    signed_by: z.string().nullish(),
    signature: z.string().nullish(),
  })
  .nullish();
export type Distribution = z.infer<typeof Distribution>;

// ── ADR-009 optional sub-models ─────────────────────────────────────

export const LinkEntry = z
  .object({
    target: z.string().min(1),
    relation: LinkRelation.default("see-also"),
    weight: z.number().min(0).max(1).nullish(),
  })
  .strict();
export type LinkEntry = z.infer<typeof LinkEntry>;

// kind=memory_neuron's published frontmatter contract is exactly five
// fields. Freeform extras belong on capture_sessions.context_md, not on
// the published neuron file. (Wave-1 added a `context` field here; it
// was removed in Wave-2 per ADR-009.)
export const NeuronBlock = z
  .object({
    situation: z.string().min(1),
    decision: z.string().min(1),
    outcome: z.string().min(1),
    recorded_at: z.string().nullish(),
    confidence: z.number().min(0).max(1).nullish(),
  })
  .strict();
export type NeuronBlock = z.infer<typeof NeuronBlock>;

// ── Root frontmatter ────────────────────────────────────────────────

export const SEMVER_RE = /^\d+\.\d+\.\d+(?:-[\w.]+)?$/;
export const ID_RE = /^[a-z0-9-]+\/[a-z0-9-]+$/;

export const SkillFrontmatter = z
  .object({
    // Identity
    id: z.string().regex(ID_RE),
    version: z.string().regex(SEMVER_RE),
    name: z.string().max(80),
    description: z.string().max(280).refine((s) => !/[\r\n]/.test(s), {
      message: "description must be a single line",
    }),

    // Authorship
    authors: z.array(Author).default([]),

    // Marketplace metadata
    category: z.string(),
    tags: z.array(z.string()).max(10).default([]),
    license_type: LicenseType,
    pricing: Pricing.nullish(),

    // AI requirements
    ai: AiBlock,

    // Discoverability
    trigger_keywords: z.array(z.string()).max(20).default([]),
    example_invocations: z.array(z.string()).max(5).default([]),

    // I/O
    inputs: z.array(SkillInput).default([]),
    outputs: z.array(SkillOutput).default([]),

    // Versioning
    changelog: z.array(ChangelogEntry).default([]),

    // Distribution (platform-set)
    distribution: Distribution,

    // ── ADR-009 optional fields ───────────────────────────────────
    kind: SkillKind.default("skill"),
    links: z.array(LinkEntry).default([]),
    parent_occupation_id: z.string().nullish(),
    neuron: NeuronBlock.nullish(),
    // Set by the vault-builder. Creators MUST NOT supply this.
    vault_path: z.string().nullish(),
  })
  .strict();
export type SkillFrontmatter = z.infer<typeof SkillFrontmatter>;
