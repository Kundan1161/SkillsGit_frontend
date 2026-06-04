/**
 * Typed fetch wrappers for the catalog + skill detail + creator profile
 * endpoints. Placeholder until ``pnpm codegen`` regenerates the typed
 * client from the OpenAPI schema — same call signatures will work.
 *
 * Used by RSC pages (server fetch) and TanStack Query (client fetch).
 */

import { api } from "@/lib/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Shared types (mirrors src/catalog/schemas.py) ─────────────────

export interface CreatorChip {
  handle: string;
  display_name: string | null;
  avatar_url: string | null;
  is_verified: boolean;
}

export interface SkillCardItem {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  cover_image_url: string | null;
  category: string | null;
  description_snippet?: string | null;
  tags: string[];
  pricing_model: "free" | "one_time" | "subscription" | "freemium";
  one_time_price_cents: number | null;
  subscription_price_cents: number | null;
  rating_avg: number | null;
  rating_count: number;
  total_sales: number;
  creator: CreatorChip;
  latest_version: string | null;
  released_at: string | null;
}

export interface PageInfo {
  next_cursor: string | null;
  has_more: boolean;
  limit: number;
}

export interface SkillCardPage {
  items: SkillCardItem[];
  page: PageInfo;
}

export interface CategoryItem {
  slug: string;
  name: string;
  description: string | null;
  parent_slug: string | null;
  display_order: number;
  skill_count: number;
}

export interface CategoryList {
  items: CategoryItem[];
}

export interface FeaturedItem {
  id: string;
  slot: string | null;
  sort_order: number;
  starts_at: string | null;
  ends_at: string | null;
  skill: SkillCardItem;
}

export interface FeaturedList {
  items: FeaturedItem[];
}

export interface SkillPricing {
  model: "free" | "one_time" | "subscription" | "freemium";
  one_time_price_cents: number | null;
  subscription_price_cents: number | null;
  currency: string;
  support_included: boolean;
  freemium_paired_with: string | null;
}

export interface AiRequirements {
  required_models: string[];
  compatible_models: string[];
  tools_required: string[];
  min_context_tokens: number | null;
  estimated_tokens_per_invocation: number | null;
}

export interface SkillDetail {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  description_md: string | null;
  category: string | null;
  tags: string[];
  cover_image_url: string | null;
  screenshots: string[];
  faq_md: string | null;
  status: "published" | "unlisted" | "draft" | "pending_review" | "removed";
  pricing: SkillPricing;
  ai_requirements: AiRequirements;
  latest_version: {
    id: string;
    version: string;
    released_at: string | null;
    changelog_md: string | null;
  } | null;
  stats: {
    rating_avg: number | null;
    rating_count: number;
    total_sales: number;
  };
  creator: CreatorChip;
  preview_body_md: string | null;
  inspired_by_urls: string[];
}

export interface VersionItem {
  id: string;
  version: string;
  released_at: string | null;
  changelog_md: string | null;
  is_yanked: boolean;
  yank_reason: string | null;
}

export interface VersionList {
  items: VersionItem[];
  page: PageInfo;
}

export interface VersionPreview {
  version: string;
  preview_body_md: string;
}

export interface CreatorStats {
  total_skills: number;
  total_sales: number;
  rating_avg: number | null;
}

export interface CreatorProfilePublic {
  handle: string;
  display_name: string | null;
  avatar_url: string | null;
  bio_md: string | null;
  website_url: string | null;
  social: Record<string, string>;
  industries: string[];
  is_verified: boolean;
  stats: CreatorStats;
}

// ── Filter / sort types ────────────────────────────────────────────

export type CatalogSort =
  | "relevance"
  | "newest"
  | "top_rated"
  | "most_sold"
  | "price_asc"
  | "price_desc";

export interface CatalogQuery {
  q?: string;
  categories?: string[];
  pricing_models?: string[];
  min_price_cents?: number;
  max_price_cents?: number;
  required_models?: string[];
  tags?: string[];
  min_rating?: number;
  creator_handle?: string;
  sort?: CatalogSort;
  limit?: number;
  cursor?: string;
}

function buildQuery(q: CatalogQuery): string {
  const params = new URLSearchParams();
  if (q.q) params.set("q", q.q);
  if (q.categories?.length) params.set("categories", q.categories.join(","));
  if (q.pricing_models?.length)
    params.set("pricing_models", q.pricing_models.join(","));
  if (q.min_price_cents != null)
    params.set("min_price_cents", String(q.min_price_cents));
  if (q.max_price_cents != null)
    params.set("max_price_cents", String(q.max_price_cents));
  if (q.required_models?.length)
    params.set("required_models", q.required_models.join(","));
  if (q.tags?.length) params.set("tags", q.tags.join(","));
  if (q.min_rating != null) params.set("min_rating", String(q.min_rating));
  if (q.creator_handle) params.set("creator_handle", q.creator_handle);
  if (q.sort) params.set("sort", q.sort);
  if (q.limit) params.set("limit", String(q.limit));
  if (q.cursor) params.set("cursor", q.cursor);
  const s = params.toString();
  return s ? `?${s}` : "";
}

// ── Server-side fetch (RSC) — uses Next's fetch cache directives ────

interface FetchOpts {
  revalidate?: number;
  tags?: string[];
}

async function ssrFetch<T>(path: string, opts: FetchOpts = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    next: {
      revalidate: opts.revalidate ?? 60,
      tags: opts.tags,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
  }
  return (await res.json()) as T;
}

async function ssrFetchOrNull<T>(
  path: string,
  opts: FetchOpts = {},
): Promise<T | null> {
  const res = await fetch(`${API_URL}${path}`, {
    next: {
      revalidate: opts.revalidate ?? 60,
      tags: opts.tags,
    },
  });
  if (res.status === 404) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
  }
  return (await res.json()) as T;
}

// ── Public API ───────────────────────────────────────────────────

export const catalogApi = {
  listSkills(query: CatalogQuery = {}, opts: FetchOpts = {}) {
    return ssrFetch<SkillCardPage>(
      `/v1/catalog/skills${buildQuery(query)}`,
      opts,
    );
  },
  listSkillsSafe(query: CatalogQuery = {}, opts: FetchOpts = {}) {
    return ssrFetch<SkillCardPage>(
      `/v1/catalog/skills${buildQuery(query)}`,
      opts,
    ).catch(() => ({ items: [], page: { has_more: false, limit: 20, next_cursor: null } }));
  },
  listCategories(opts: FetchOpts = {}) {
    return ssrFetch<CategoryList>("/v1/catalog/categories", opts).catch(
      () => ({ items: [] }),
    );
  },
  listFeatured(opts: FetchOpts = {}) {
    return ssrFetch<FeaturedList>("/v1/catalog/featured", opts).catch(
      () => ({ items: [] }),
    );
  },

  getSkill(id_or_handleslug: string, opts: FetchOpts = {}) {
    // ``handle/slug`` form must be URL-encoded as a single segment.
    const segment = encodeURIComponent(id_or_handleslug);
    return ssrFetchOrNull<SkillDetail>(`/v1/skills/${segment}`, opts);
  },
  getSkillByHandle(handle: string, slug: string, opts: FetchOpts = {}) {
    return ssrFetchOrNull<SkillDetail>(
      `/v1/skills/by-handle/${encodeURIComponent(handle)}/${encodeURIComponent(slug)}`,
      opts,
    );
  },
  listVersions(skillId: string, opts: FetchOpts = {}) {
    return ssrFetch<VersionList>(`/v1/skills/${skillId}/versions`, opts);
  },
  getVersionPreview(skillId: string, version: string, opts: FetchOpts = {}) {
    return ssrFetch<VersionPreview>(
      `/v1/skills/${skillId}/versions/${encodeURIComponent(version)}/preview`,
      opts,
    );
  },

  getCreator(handle: string, opts: FetchOpts = {}) {
    return ssrFetchOrNull<CreatorProfilePublic>(
      `/v1/creators/${encodeURIComponent(handle)}`,
      opts,
    );
  },
  listCreatorSkills(handle: string, query: CatalogQuery = {}, opts: FetchOpts = {}) {
    return ssrFetch<SkillCardPage>(
      `/v1/creators/${encodeURIComponent(handle)}/skills${buildQuery(query)}`,
      opts,
    );
  },
};

// Client-side hook helpers re-use `api` from lib/api.ts for credentials.
export const catalogClientApi = {
  searchSuggest: (q: string) =>
    api.get<SkillCardPage>(`/v1/catalog/skills?q=${encodeURIComponent(q)}&limit=5`),
  createSearchAlert: (body: { name?: string; query?: string; filters: Record<string, unknown> }) =>
    api.post(`/v1/catalog/search-alerts`, body),
};

// ── Formatting helpers ───────────────────────────────────────────


export function formatPrice(skill: Pick<SkillCardItem, "pricing_model" | "one_time_price_cents" | "subscription_price_cents">): string {
  if (skill.pricing_model === "free") return "Free";
  if (skill.pricing_model === "subscription") {
    const cents = skill.subscription_price_cents ?? 0;
    return `$${(cents / 100).toFixed(0)}/mo`;
  }
  const cents = skill.one_time_price_cents ?? 0;
  return `$${(cents / 100).toFixed(0)}`;
}

export function priceCta(skill: Pick<SkillCardItem, "pricing_model" | "one_time_price_cents" | "subscription_price_cents">): string {
  if (skill.pricing_model === "free") return "Get free version";
  if (skill.pricing_model === "subscription") {
    const cents = skill.subscription_price_cents ?? 0;
    return `Subscribe — $${(cents / 100).toFixed(0)}/mo`;
  }
  const cents = skill.one_time_price_cents ?? 0;
  return `Buy for $${(cents / 100).toFixed(0)}`;
}

export function categoryLabel(slug: string | null | undefined): string {
  if (!slug) return "";
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
