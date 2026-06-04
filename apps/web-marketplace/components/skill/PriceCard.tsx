import Link from "next/link";
import { Lock, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import {
  formatPrice,
  priceCta,
  type SkillDetail,
} from "@/lib/api/catalog";

export interface PriceCardProps {
  skill: SkillDetail;
  ownsSkill?: boolean;
  licenseId?: string | null;
}

export function PriceCard({ skill, ownsSkill, licenseId }: PriceCardProps) {
  const checkoutHref = `/checkout?skill=${skill.id}`;
  return (
    <Card aria-label="Pricing" className="border-none" style={{ borderRadius: "1.25rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-lg)" }}>
      <CardHeader className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Badge variant="outline">
            {skill.pricing.model === "free"
              ? "Free"
              : skill.pricing.model === "subscription"
                ? "Subscription"
                : skill.pricing.model === "freemium"
                  ? "Freemium"
                  : "One-time"}
          </Badge>
          {skill.pricing.support_included ? (
            <Badge variant="secondary" className="gap-1">
              <Sparkles className="h-3 w-3" /> Support included
            </Badge>
          ) : null}
        </div>
        <div className="text-3xl font-semibold tracking-tight text-price">
          {formatPrice({
            pricing_model: skill.pricing.model,
            one_time_price_cents: skill.pricing.one_time_price_cents,
            subscription_price_cents: skill.pricing.subscription_price_cents,
          })}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {ownsSkill ? (
          <Button asChild size="lg" className="w-full neu-btn-brand border-none hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 text-white font-bold" style={{ borderRadius: "1rem" }}>
            <Link href={licenseId ? `/library/${licenseId}` : "/library"}>
              Open in library
            </Link>
          </Button>
        ) : (
          <Button asChild size="lg" className="w-full neu-btn-brand border-none hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 text-white font-bold" style={{ borderRadius: "1rem" }}>
            <Link href={checkoutHref}>
              {priceCta({
                pricing_model: skill.pricing.model,
                one_time_price_cents: skill.pricing.one_time_price_cents,
                subscription_price_cents: skill.pricing.subscription_price_cents,
              })}
            </Link>
          </Button>
        )}
        <Button asChild variant="outline" size="lg" className="w-full neu-btn border-none hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 text-fg font-bold" style={{ borderRadius: "1rem" }}>
          <Link href={`/sign-in?next=/s/${skill.creator.handle}/${skill.slug}`}>
            <Lock className="mr-2 h-4 w-4" />
            Try in sandbox
          </Link>
        </Button>
        <button
          type="button"
          className="block w-full text-center text-xs text-fg-muted hover:underline"
        >
          Add to wishlist
        </button>
      </CardContent>
      <CardFooter className="block space-y-1 border-t border-border pt-4 text-xs text-fg-subtle">
        <p>Currency: {skill.pricing.currency}</p>
        {skill.latest_version ? (
          <p>
            Latest: v{skill.latest_version.version}
            {skill.latest_version.released_at
              ? ` · released ${new Date(skill.latest_version.released_at).toLocaleDateString()}`
              : ""}
          </p>
        ) : null}
      </CardFooter>
    </Card>
  );
}
