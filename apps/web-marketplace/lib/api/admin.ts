/**
 * Admin moderation API wrappers.
 *
 * See `prompts/marketplace/05-trust-and-quality.md`.
 */
import { api } from "@/lib/api";

export type SkillStatus =
  | "draft"
  | "pending_review"
  | "published"
  | "unlisted"
  | "removed";

export interface ModerationQueueItem {
  skill_id: string;
  name: string;
  slug: string;
  status: SkillStatus;
  creator_handle: string | null;
  creator_display_name: string | null;
  submitted_version: string | null;
  submitted_at: string | null;
  rejection_reason: string | null;
  cover_image_url: string | null;
}

export interface ModerationQueueList {
  items: ModerationQueueItem[];
  page: { next_cursor: string | null; has_more: boolean; limit: number };
}

export interface ApprovalResponse {
  skill_id: string;
  status: SkillStatus;
  version: string | null;
  moderation_action_id: string;
}

export interface AdminUserSummary {
  id: string;
  email: string;
  display_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  is_creator_verified: boolean;
  creator_handle: string | null;
  created_at: string;
}

export interface AdminUserList {
  items: AdminUserSummary[];
  page: { next_cursor: string | null; has_more: boolean; limit: number };
}

export const adminApi = {
  moderationQueue: () =>
    api.get<ModerationQueueList>("/v1/admin/moderation"),

  approveSkill: (id: string) =>
    api.post<ApprovalResponse>(`/v1/admin/skills/${id}/approve`),

  rejectSkill: (id: string, reason: string) =>
    api.post<ApprovalResponse>(`/v1/admin/skills/${id}/reject`, { reason }),

  listUsers: (q?: string) => {
    const qs = q ? `?q=${encodeURIComponent(q)}` : "";
    return api.get<AdminUserList>(`/v1/admin/users${qs}`);
  },

  verifyCreator: (userId: string) =>
    api.post<AdminUserSummary>(`/v1/admin/users/${userId}/verify-creator`),

  suspendUser: (userId: string, reason?: string) =>
    api.post<AdminUserSummary>(`/v1/admin/users/${userId}/suspend`, {
      reason,
    }),
};
