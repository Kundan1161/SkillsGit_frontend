/**
 * Typed wrappers around the billing endpoints.
 *
 * Backend spec: `prompts/marketplace/03-pricing-and-checkout.md`.
 * These thin wrappers will be replaced by the generated `@skillsgit/api-client`
 * after `pnpm codegen` runs; until then this module is the single source of
 * truth for shapes.
 */

import { api } from "../api";

// ── Request types ─────────────────────────────────────────────────────
export interface CreateCheckoutSessionRequest {
  skill_id: string;
  idempotency_key?: string;
}

export interface StartOnboardingRequest {
  payout_country: string;
}

export interface RefundRequest {
  reason?: string;
}

// ── Response types ────────────────────────────────────────────────────
export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface FinalizeResponse {
  session_id: string;
  status: "open" | "complete" | "expired" | "failed" | "pending" | string;
  order_id: string | null;
  license_id: string | null;
}

export interface OnboardingStartResponse {
  url: string;
  account_id: string;
}

export interface OnboardingStatusResponse {
  account_id: string | null;
  details_submitted: boolean;
  payouts_enabled: boolean;
  charges_enabled: boolean;
}

export interface BillingPortalResponse {
  url: string;
}

export interface PriceBreakdown {
  amount_cents: number;
  platform_fee_cents: number;
  creator_payout_cents: number;
  currency: string;
}

export interface OrderItemRead {
  id: string;
  skill_id: string;
  skill_version_id: string;
  price_cents: number;
  platform_fee_cents: number;
  creator_id: string;
}

export interface OrderRead {
  id: string;
  buyer_id: string;
  status: string;
  subtotal_cents: number;
  platform_fee_cents: number;
  creator_payout_cents: number;
  currency: string;
  placed_at: string | null;
  stripe_payment_intent_id: string | null;
  items: OrderItemRead[];
}

export interface OrderListResponse {
  items: OrderRead[];
  page: { next_cursor: string | null; has_more: boolean; limit: number };
}

// ── Helpers ───────────────────────────────────────────────────────────
function randomIdempotencyKey(): string {
  // RFC 4122 v4-ish; sufficient for the 24h dedup window.
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `idem_${Math.random().toString(36).slice(2)}${Date.now()}`;
}

// ── Endpoints ─────────────────────────────────────────────────────────
export const billing = {
  /** Create a Stripe Checkout session for a one-time skill purchase. */
  createCheckoutSession: async (
    body: CreateCheckoutSessionRequest,
  ): Promise<CheckoutSessionResponse> => {
    const idemKey = body.idempotency_key ?? randomIdempotencyKey();
    return api.post<CheckoutSessionResponse>(
      "/v1/checkout/sessions",
      { ...body, idempotency_key: idemKey },
      { headers: { "Idempotency-Key": idemKey } },
    );
  },

  /** Poll a checkout session until the webhook lands. */
  finalizeCheckoutSession: (sessionId: string) =>
    api.post<FinalizeResponse>(
      `/v1/checkout/sessions/${encodeURIComponent(sessionId)}/finalize`,
    ),

  /** Resolve an order from a Stripe Checkout Session id. */
  getOrderBySession: (sessionId: string) =>
    api.get<OrderRead | null>(
      `/v1/orders/by-session/${encodeURIComponent(sessionId)}`,
    ),

  /** List current user's orders. */
  listMyOrders: (limit = 20) =>
    api.get<OrderListResponse>(`/v1/orders/me?limit=${limit}`),

  /** Request a refund for a one-time order. */
  refundOrder: async (orderId: string, body: RefundRequest = {}) => {
    const idemKey = randomIdempotencyKey();
    return api.post<{ status: string }>(
      `/v1/orders/${encodeURIComponent(orderId)}/refund`,
      body,
      { headers: { "Idempotency-Key": idemKey } },
    );
  },

  /** Start (or continue) Stripe Connect Express onboarding for a creator. */
  startOnboarding: (body: StartOnboardingRequest) =>
    api.post<OnboardingStartResponse>(
      "/v1/creator/onboarding/start",
      body,
    ),

  /** Re-fetch Stripe Connect account status. */
  getOnboardingStatus: () =>
    api.get<OnboardingStatusResponse>("/v1/creator/onboarding/status"),

  /** Open the Stripe Customer billing portal. */
  openBillingPortal: () =>
    api.post<BillingPortalResponse>("/v1/billing/portal-session"),

  /** Compute platform-fee breakdown for a price (helper). */
  previewPrice: (amountCents: number) =>
    api.get<PriceBreakdown>(`/v1/billing/preview?amount_cents=${amountCents}`),
};
