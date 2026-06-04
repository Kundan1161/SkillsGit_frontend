"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import {
  CheckoutSummary,
  StripeRedirectButton,
} from "@/components/checkout";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

import { api, type ApiError } from "@/lib/api";

interface SkillSnapshot {
  id: string;
  name: string;
  tagline?: string | null;
  one_time_price_cents: number | null;
  pricing_model: string;
  status: string;
}

interface MeResponse {
  id: string;
  email: string;
}

function CheckoutInner() {
  const router = useRouter();
  const params = useSearchParams();
  const skillId = params.get("skill");
  const canceled = params.get("canceled") === "1";

  const [skill, setSkill] = useState<SkillSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!skillId) {
      setError("Missing ?skill=… query parameter.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    // Auth-gate first.
    api
      .get<MeResponse>("/v1/auth/me")
      .catch((err: ApiError) => {
        if (err.status === 401) {
          const returnTo = encodeURIComponent(`/checkout?skill=${skillId}`);
          router.replace(`/sign-in?returnTo=${returnTo}`);
          return null;
        }
        throw err;
      })
      .then((me) => {
        if (!me || cancelled) return null;
        return api.get<SkillSnapshot>(`/v1/skills/${skillId}`);
      })
      .then((s) => {
        if (!s || cancelled) return;
        setSkill(s);
        setLoading(false);
      })
      .catch((err: ApiError) => {
        if (cancelled) return;
        setError(err.message || "Could not load checkout.");
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [skillId, router]);

  if (loading) {
    return (
      <section className="mx-auto max-w-4xl px-4 py-12 md:px-8">
        <div className="grid gap-8 md:grid-cols-[1fr_360px]">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-72 w-full" />
        </div>
      </section>
    );
  }

  if (error || !skill) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-16 md:px-0">
        <Alert variant="destructive">
          <AlertTitle>Checkout unavailable</AlertTitle>
          <AlertDescription>
            {error ?? "Skill not found."} —{" "}
            <Link href="/browse" className="underline">
              return to browse
            </Link>
            .
          </AlertDescription>
        </Alert>
      </section>
    );
  }

  if (skill.pricing_model !== "one_time" || !skill.one_time_price_cents) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-16 md:px-0">
        <Alert>
          <AlertTitle>Not a one-time purchase</AlertTitle>
          <AlertDescription>
            This skill is{" "}
            <code className="font-mono text-xs">{skill.pricing_model}</code>.
            Checkout only handles one-time purchases in this phase.
          </AlertDescription>
        </Alert>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-4xl px-4 py-12 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight">Checkout</h1>
      <p className="mt-2 text-fg-muted">
        Complete your purchase securely on Stripe.
      </p>

      {canceled ? (
        <Alert className="mt-6">
          <AlertTitle>Payment canceled</AlertTitle>
          <AlertDescription>
            You can try again whenever you're ready — no charge was made.
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="mt-8 grid gap-8 md:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{skill.name}</CardTitle>
            {skill.tagline ? (
              <CardDescription>{skill.tagline}</CardDescription>
            ) : null}
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-fg-muted">
              You'll be redirected to Stripe's secure checkout. After payment
              we'll bring you back to your library to download the skill.
            </p>
            <StripeRedirectButton
              skillId={skill.id}
              size="lg"
              className="w-full"
              onError={(err) => {
                setError(
                  (err as { message?: string })?.message ??
                    "Could not start checkout.",
                );
              }}
            >
              Continue to payment
            </StripeRedirectButton>
          </CardContent>
        </Card>

        <CheckoutSummary
          skillName={skill.name}
          skillTagline={skill.tagline}
          amountCents={skill.one_time_price_cents}
        />
      </div>
    </section>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={null}>
      <CheckoutInner />
    </Suspense>
  );
}
