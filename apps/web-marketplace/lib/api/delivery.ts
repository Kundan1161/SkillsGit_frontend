/**
 * Library / delivery API wrappers.
 *
 * Eventually superseded by the generated client from `@skillsgit/api-client`
 * (`pnpm codegen`). For now these are hand-typed so the UI compiles.
 */
import { api } from "@/lib/api";

export type LicenseSource =
  | "one_time"
  | "subscription"
  | "free"
  | "freemium"
  | "grant";

export type LicenseStatus = "active" | "expired" | "revoked";

export type SupportTier = "none" | "basic" | "priority";

export interface LicenseVersionInfo {
  id: string;
  version: string;
  released_at: string | null;
  is_yanked: boolean;
}

export interface LicenseSkillInfo {
  id: string;
  name: string;
  slug: string;
  creator_handle: string | null;
  creator_display_name: string | null;
  cover_image_url: string | null;
}

export interface LicenseRead {
  id: string;
  skill: LicenseSkillInfo;
  source: LicenseSource;
  status: LicenseStatus;
  support_tier: SupportTier;
  granted_at: string;
  expires_at: string | null;
  max_version: string | null;
  current_version: LicenseVersionInfo | null;
  last_downloaded_at: string | null;
  download_count: number;
}

export interface LicenseList {
  items: LicenseRead[];
  page: { next_cursor: string | null; has_more: boolean; limit: number };
}

export interface DownloadResponse {
  download_url: string;
  version: string;
  expires_at: string;
  content_hash: string;
}

export const deliveryApi = {
  listMyLicenses: (params?: { cursor?: string; source?: LicenseSource }) => {
    const qs = new URLSearchParams();
    if (params?.cursor) qs.set("cursor", params.cursor);
    if (params?.source) qs.set("source", params.source);
    const path = `/v1/me/licenses${qs.toString() ? `?${qs}` : ""}`;
    return api.get<LicenseList>(path);
  },

  getLicense: (id: string) => api.get<LicenseRead>(`/v1/licenses/${id}`),

  prepareDownload: (id: string) =>
    api.get<DownloadResponse>(`/v1/licenses/${id}/download`),

  prepareDownloadVersion: (id: string, version: string) =>
    api.get<DownloadResponse>(`/v1/licenses/${id}/download/${version}`),
};
