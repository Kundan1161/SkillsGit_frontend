"use client";

import { cn } from "@/lib/utils";

export interface PriceTagProps {
  amountCents: number;
  currency?: string;
  className?: string;
  /** Optional secondary line, e.g. "+ tax" or "per month". */
  suffix?: string;
}

/**
 * Renders an integer-cents amount as a localized money string.
 * Always treat the value as cents — never floats — per
 * `prompts/marketplace/03-pricing-and-checkout.md`.
 */
export function PriceTag({
  amountCents,
  currency = "USD",
  className,
  suffix,
}: PriceTagProps) {
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  });
  return (
    <span className={cn("font-semibold tabular-nums", className)}>
      {formatter.format(amountCents / 100)}
      {suffix ? (
        <span className="ml-1 text-sm font-normal text-fg-muted">{suffix}</span>
      ) : null}
    </span>
  );
}
