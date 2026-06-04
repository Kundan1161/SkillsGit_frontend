"use client";

import { useEffect, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";

import { billing, type PriceBreakdown } from "@/lib/api/billing";

import { PriceTag } from "./price-tag";

export interface CheckoutSummaryProps {
  skillName: string;
  skillTagline?: string | null;
  amountCents: number;
  currency?: string;
}

/**
 * Right-rail order summary on `/checkout`. Shows the price the buyer pays
 * and (for transparency) the platform fee breakdown that goes to creator
 * vs. platform.
 */
export function CheckoutSummary({
  skillName,
  skillTagline,
  amountCents,
  currency = "USD",
}: CheckoutSummaryProps) {
  const [breakdown, setBreakdown] = useState<PriceBreakdown | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    billing
      .previewPrice(amountCents)
      .then((b) => {
        if (!cancelled) {
          setBreakdown(b);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [amountCents]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Order summary</CardTitle>
        <CardDescription>One-time purchase</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="font-medium">{skillName}</div>
          {skillTagline ? (
            <p className="mt-1 text-sm text-fg-muted">{skillTagline}</p>
          ) : null}
        </div>
        <Separator />
        <div className="flex items-center justify-between text-sm">
          <span className="text-fg-muted">Subtotal</span>
          <PriceTag amountCents={amountCents} currency={currency} />
        </div>
        <Separator />
        <div className="flex items-center justify-between text-base">
          <span className="font-medium">Total due today</span>
          <PriceTag
            amountCents={amountCents}
            currency={currency}
            className="text-lg"
          />
        </div>
        {loading ? (
          <Skeleton className="h-3 w-2/3" />
        ) : breakdown ? (
          <p className="text-xs text-fg-muted">
            Creator receives{" "}
            <PriceTag
              amountCents={breakdown.creator_payout_cents}
              currency={currency}
              className="font-medium"
            />{" "}
            after our platform fee of{" "}
            <PriceTag
              amountCents={breakdown.platform_fee_cents}
              currency={currency}
              className="font-medium"
            />
            .
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
