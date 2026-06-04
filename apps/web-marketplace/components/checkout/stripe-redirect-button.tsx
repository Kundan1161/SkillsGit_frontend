"use client";

import { useState } from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

import { billing } from "@/lib/api/billing";

export interface StripeRedirectButtonProps
  extends Omit<ButtonProps, "onClick" | "children"> {
  skillId: string;
  children?: React.ReactNode;
  onError?: (err: unknown) => void;
}

/**
 * "Continue to payment" button. Creates a Stripe Checkout session via the
 * API, then `window.location.assign`s the buyer over to Stripe.
 *
 * Uses an Idempotency-Key (generated inside `billing.createCheckoutSession`)
 * so accidental double-clicks don't create duplicate sessions.
 */
export function StripeRedirectButton({
  skillId,
  children,
  onError,
  disabled,
  ...buttonProps
}: StripeRedirectButtonProps) {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    if (loading) return;
    setLoading(true);
    try {
      const res = await billing.createCheckoutSession({ skill_id: skillId });
      window.location.assign(res.checkout_url);
    } catch (err) {
      setLoading(false);
      onError?.(err);
    }
  }

  return (
    <Button
      {...buttonProps}
      disabled={disabled || loading}
      onClick={handleClick}
    >
      {loading ? (
        <>
          <Spinner className="size-4" />
          <span>Redirecting…</span>
        </>
      ) : (
        children ?? "Continue to payment"
      )}
    </Button>
  );
}
