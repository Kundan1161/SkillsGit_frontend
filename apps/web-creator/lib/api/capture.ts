/**
 * Typed fetch wrappers for the capture endpoint group.
 * Mirrors the structure of lib/api.ts placeholder until codegen runs.
 */
import { api } from "@/lib/api";

export type CaptureSessionStatus =
  | "draft"
  | "extracting"
  | "draft_ready"
  | "finalizing"
  | "finalized"
  | "abandoned";

export interface CaptureSessionRead {
  id: string;
  persona_id: string;
  title: string;
  situation_md: string | null;
  decision_md: string | null;
  outcome_md: string | null;
  context_md: string | null;
  status: CaptureSessionStatus;
  draft_md: string | null;
  suggested_links_json: SuggestedLink[] | null;
  pii_flags_json: PiiFlag[] | null;
  finalized_neuron_skill_id: string | null;
  finalized_at: string | null;
  llm_model: string | null;
  created_at: string;
  updated_at: string;
}

export interface SuggestedLink {
  skill_id: string;
  skill_name: string;
  skill_slug: string;
  relevance: number;
  accepted: boolean;
}

export interface PiiFlag {
  span: string;
  kind: string;
  severity: "low" | "medium" | "high";
  suggestion: string | null;
}

export interface CaptureSessionCreate {
  persona_id: string;
  title: string;
  situation_md?: string;
  decision_md?: string;
  outcome_md?: string;
  context_md?: string;
}

export interface CaptureSessionUpdate {
  title?: string;
  situation_md?: string;
  decision_md?: string;
  outcome_md?: string;
  context_md?: string;
}

export interface CaptureFinalize {
  accepted_link_skill_ids?: string[];
}

export interface JobAccepted {
  job_id: string;
  status: string;
}

export interface NeuronCreated {
  neuron_skill_id: string;
  vault_path: string | null;
}

export const captureApi = {
  createSession: (payload: CaptureSessionCreate) =>
    api.post<CaptureSessionRead>("/v1/capture/sessions", payload),

  getSession: (id: string) =>
    api.get<CaptureSessionRead>(`/v1/capture/sessions/${id}`),

  updateSession: (id: string, payload: CaptureSessionUpdate) =>
    api.patch<CaptureSessionRead>(`/v1/capture/sessions/${id}`, payload),

  listSessions: (params?: { persona_id?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (params?.persona_id) qs.set("persona_id", params.persona_id);
    if (params?.status) qs.set("status", params.status);
    const suffix = qs.size ? `?${qs}` : "";
    return api.get<{ items: CaptureSessionRead[]; page: { has_more: boolean } }>(
      `/v1/capture/sessions${suffix}`,
    );
  },

  triggerExtract: (id: string) =>
    api.post<JobAccepted>(`/v1/capture/sessions/${id}/extract`),

  finalize: (id: string, payload: CaptureFinalize) =>
    api.post<NeuronCreated>(`/v1/capture/sessions/${id}/finalize`, payload),

  abandon: (id: string) =>
    api.post<void>(`/v1/capture/sessions/${id}/abandon`),
};
