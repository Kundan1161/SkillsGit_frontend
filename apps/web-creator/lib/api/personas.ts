/**
 * Typed fetch wrappers for the personas + occupations endpoint groups
 * (creator side). Used by the persona admin pages.
 */
import { api } from "@/lib/api";

export interface PersonaRead {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  creator_intro_md: string | null;
  years_of_experience: number | null;
  specialization: string | null;
  neuron_count: number;
  status: "draft" | "pending_review" | "published" | "unlisted";
  parent_occupation_id: string;
  parent_occupation_name: string;
  latest_build_id: string | null;
  created_at: string;
}

export interface PersonaCreate {
  parent_occupation_id: string;
  name: string;
  tagline?: string;
  creator_intro_md?: string;
  years_of_experience?: number;
  specialization?: string;
  pricing_model: "one_time" | "subscription" | "free";
  one_time_price_cents?: number;
  subscription_price_cents?: number;
}

export interface PersonaUpdate {
  name?: string;
  tagline?: string;
  creator_intro_md?: string;
  years_of_experience?: number;
  specialization?: string;
}

export interface NeuronRead {
  id: string;
  slug: string;
  name: string;
  tagline: string | null;
  vault_path: string | null;
  sort_order: number;
  section: string | null;
  capture_session_id: string | null;
}

export interface OccupationOption {
  id: string;
  slug: string;
  name: string;
  creator_handle: string;
}

export const personasCreatorApi = {
  list: () =>
    api.get<{ items: PersonaRead[] }>("/v1/personas/mine"),

  get: (id: string) =>
    api.get<PersonaRead>(`/v1/personas/${id}`),

  create: (payload: PersonaCreate) =>
    api.post<PersonaRead>("/v1/personas", payload),

  update: (id: string, payload: PersonaUpdate) =>
    api.patch<PersonaRead>(`/v1/personas/${id}`, payload),

  publish: (id: string, version: string) =>
    api.post<{ job_id: string }>(`/v1/personas/${id}/publish`, { version }),

  listNeurons: (personaId: string) =>
    api.get<{ items: NeuronRead[] }>(`/v1/personas/${personaId}/neurons`),

  reorderNeurons: (
    personaId: string,
    items: { neuron_skill_id: string; sort_order: number }[],
  ) => api.post<void>(`/v1/personas/${personaId}/neurons/order`, { items }),

  removeNeuron: (personaId: string, neuronId: string) =>
    api.delete<void>(`/v1/personas/${personaId}/neurons/${neuronId}`),

  triggerBuild: (personaId: string) =>
    api.post<{ job_id: string }>(`/v1/personas/${personaId}/build`),
};

export const occupationsCreatorApi = {
  listPublished: () =>
    api.get<{ items: OccupationOption[] }>(
      "/v1/occupations?status=published&limit=100",
    ),
};
