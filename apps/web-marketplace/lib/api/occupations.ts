/**
 * Typed fetch wrappers for occupation + persona endpoints.
 * Mirrors the catalog.ts pattern; will be replaced by codegen.
 */

import { api } from "@/lib/api";

// ── Shared types (mirrors src/occupations/schemas.py) ────────────────

export interface OccupationSkillRead {
  id: string;
  member_skill_id: string;
  domain: string;
  sort_order: number;
  role: "core" | "supporting" | "optional";
  pinned: boolean;
  notes_md: string | null;
  skill: {
    id: string;
    slug: string;
    name: string;
    tagline: string | null;
    creator_handle: string;
  };
}

export interface OccupationRead {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  summary_md: string | null;
  domains: string[];
  persona_count: number;
  status: string;
  cover_image_url: string | null;
  creator: { handle: string; display_name: string | null };
  latest_version: string | null;
  pricing: {
    model: string;
    one_time_price_cents: number | null;
    subscription_price_cents: number | null;
    currency: string;
  };
  stats: { total_sales: number; rating_avg: number | null; rating_count: number };
}

export interface OccupationDetailResponse extends OccupationRead {
  members: OccupationSkillRead[];
}

export interface OccupationListResponse {
  items: OccupationRead[];
  page: { next_cursor: string | null; has_more: boolean; limit: number };
}

export interface PersonaRead {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  creator_intro_md: string | null;
  years_of_experience: number | null;
  specialization: string | null;
  neuron_count: number;
  status: string;
  cover_image_url: string | null;
  creator: { handle: string; display_name: string | null; avatar_url: string | null };
  parent_occupation: { id: string; slug: string; name: string; creator_handle: string };
  pricing: {
    model: string;
    one_time_price_cents: number | null;
    subscription_price_cents: number | null;
    currency: string;
  };
  stats: { total_sales: number; rating_avg: number | null; rating_count: number };
}

export interface NeuronSnippet {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  vault_path: string | null;
}

export interface PersonaDetailResponse extends PersonaRead {
  neurons: NeuronSnippet[];
}

// ── API helpers ───────────────────────────────────────────────────────

export const occupationsApi = {
  async getByHandle(
    handle: string,
    slug: string,
  ): Promise<OccupationDetailResponse | null> {
    try {
      return await api.get<OccupationDetailResponse>(
        `/v1/occupations/${handle}/${slug}`,
      );
    } catch {
      return null;
    }
  },

  async list(params?: {
    q?: string;
    limit?: number;
    cursor?: string;
  }): Promise<OccupationListResponse> {
    const qs = new URLSearchParams();
    if (params?.q) qs.set("q", params.q);
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.cursor) qs.set("cursor", params.cursor);
    const suffix = qs.size ? `?${qs}` : "";
    return api.get<OccupationListResponse>(`/v1/occupations${suffix}`);
  },
};

export const personasApi = {
  async getByHandle(
    handle: string,
    slug: string,
  ): Promise<PersonaDetailResponse | null> {
    try {
      return await api.get<PersonaDetailResponse>(
        `/v1/personas/${handle}/${slug}`,
      );
    } catch {
      return null;
    }
  },

  async listForOccupation(occupationId: string): Promise<PersonaRead[]> {
    try {
      const res = await api.get<{ items: PersonaRead[] }>(
        `/v1/personas?occupation_id=${occupationId}&status=published`,
      );
      return res.items;
    } catch {
      return [];
    }
  },
};
