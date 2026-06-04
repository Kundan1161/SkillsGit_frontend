/**
 * Creator-side skill management API wrappers.
 *
 * See `prompts/marketplace/07-creator-dashboard.md` (Phase 1 upload path).
 */
import { api, type ApiError } from "@/lib/api";

export type PricingModel = "free" | "one_time" | "subscription" | "freemium";

export type SkillStatus =
  | "draft"
  | "pending_review"
  | "published"
  | "unlisted"
  | "removed";

export interface SkillRead {
  id: string;
  creator_id: string;
  slug: string;
  name: string;
  tagline: string | null;
  description_md: string | null;
  category: string | null;
  tags: string[] | null;
  cover_image_url: string | null;
  screenshots: string[] | null;
  status: SkillStatus;
  latest_version_id: string | null;
  pricing_model: PricingModel;
  one_time_price_cents: number | null;
  subscription_price_cents: number | null;
  support_included: boolean;
  total_sales: number;
  rating_avg: string | null;
  rating_count: number;
  created_at: string;
  updated_at: string;
}

export interface SkillVersionRead {
  id: string;
  skill_id: string;
  version: string;
  content_hash: string;
  storage_url: string;
  changelog_md: string | null;
  released_at: string | null;
  is_yanked: boolean;
}

export interface CreateSkillInput {
  name: string;
  tagline?: string;
  category?: string;
  tags?: string;
  pricing_model: PricingModel;
  one_time_price_cents?: number;
  support_url?: string;
  cover_image?: File | null;
  skills_md: File;
}

async function uploadFormData<T>(
  path: string,
  form: FormData,
  method: "POST" | "PATCH" = "POST",
): Promise<T> {
  const url = `${
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  }${path}`;
  const res = await fetch(url, {
    method,
    credentials: "include",
    body: form,
  });
  if (!res.ok) {
    let parsed: unknown = undefined;
    try {
      parsed = await res.json();
    } catch {
      /* ignore */
    }
    const err: ApiError = {
      status: res.status,
      code:
        (parsed as { error?: { code?: string } })?.error?.code ??
        `http_${res.status}`,
      message:
        (parsed as { error?: { message?: string } })?.error?.message ??
        res.statusText,
      details: parsed,
    };
    throw err;
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const skillsApi = {
  listMine: () => api.get<SkillRead[]>("/v1/creator/skills/"),

  create: (input: CreateSkillInput) => {
    const fd = new FormData();
    fd.set("name", input.name);
    if (input.tagline) fd.set("tagline", input.tagline);
    if (input.category) fd.set("category", input.category);
    if (input.tags) fd.set("tags", input.tags);
    fd.set("pricing_model", input.pricing_model);
    if (input.one_time_price_cents != null) {
      fd.set("one_time_price_cents", String(input.one_time_price_cents));
    }
    if (input.support_url) fd.set("support_url", input.support_url);
    if (input.cover_image) fd.set("cover_image", input.cover_image);
    fd.set("skills_md", input.skills_md);
    return uploadFormData<SkillRead>("/v1/creator/skills/", fd);
  },

  patch: (id: string, patch: Partial<SkillRead>) =>
    api.patch<SkillRead>(`/v1/creator/skills/${id}`, patch),

  submitVersion: (
    id: string,
    skillsMd: File,
    targetVersion: string,
    changelog?: string,
  ) => {
    const fd = new FormData();
    fd.set("skills_md", skillsMd);
    fd.set("target_version", targetVersion);
    if (changelog) fd.set("changelog_md", changelog);
    return uploadFormData<SkillVersionRead>(
      `/v1/creator/skills/${id}/versions`,
      fd,
    );
  },

  publish: (id: string) =>
    api.post<SkillRead>(`/v1/creator/skills/${id}/publish`),

  yank: (id: string, version: string, reason?: string) =>
    api.post<SkillVersionRead>(
      `/v1/creator/skills/${id}/versions/${version}/yank`,
      { reason },
    ),

  remove: (id: string) => api.delete<void>(`/v1/creator/skills/${id}`),
};
