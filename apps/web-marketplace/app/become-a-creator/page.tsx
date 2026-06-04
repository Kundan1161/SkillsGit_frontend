"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";

import { api, type ApiError } from "@/lib/api";
import { billing } from "@/lib/api/billing";

const COUNTRIES = [
  { code: "US", name: "United States" },
  { code: "CA", name: "Canada" },
  { code: "GB", name: "United Kingdom" },
  { code: "AU", name: "Australia" },
  { code: "DE", name: "Germany" },
  { code: "FR", name: "France" },
  { code: "IE", name: "Ireland" },
  { code: "NL", name: "Netherlands" },
  { code: "ES", name: "Spain" },
  { code: "IT", name: "Italy" },
];

type Step = "form" | "redirecting" | "verifying";

function BecomeCreatorInner() {
  const router = useRouter();
  const params = useSearchParams();
  const onboarding = params.get("onboarding");

  const [step, setStep] = useState<Step>(
    onboarding === "done" || onboarding === "incomplete"
      ? "verifying"
      : "form",
  );
  const [handle, setHandle] = useState("");
  const [country, setCountry] = useState("US");
  const [terms, setTerms] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Verification state (from Stripe return).
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [statusOk, setStatusOk] = useState<boolean | null>(null);

  // If we returned from Stripe, fetch the status to confirm payouts.
  useEffect(() => {
    if (step !== "verifying") return;
    let cancelled = false;
    setStatusMsg("Checking your payouts setup…");

    billing
      .getOnboardingStatus()
      .then((s) => {
        if (cancelled) return;
        if (s.payouts_enabled) {
          setStatusOk(true);
          setStatusMsg("Payouts enabled. You can now list paid skills.");
        } else if (s.details_submitted) {
          setStatusOk(false);
          setStatusMsg(
            "Stripe is still reviewing your details. We'll enable payouts once that's complete.",
          );
        } else {
          setStatusOk(false);
          setStatusMsg(
            "Onboarding wasn't completed. You can finish it from your creator dashboard.",
          );
        }
      })
      .catch((err: ApiError) => {
        if (cancelled) return;
        setStatusOk(false);
        setStatusMsg(err.message || "Could not load onboarding status.");
      });

    return () => {
      cancelled = true;
    };
  }, [step]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!handle.trim()) {
      setError("Pick a handle.");
      return;
    }
    if (!terms) {
      setError("You must accept the creator terms to continue.");
      return;
    }
    setSubmitting(true);
    try {
      // 1. Create the creator profile (already implemented in Phase 0).
      await api.post("/v1/auth/become-creator", {
        handle: handle.trim(),
        payout_country: country,
      });
      // 2. Start Stripe Connect onboarding.
      const onboard = await billing.startOnboarding({ payout_country: country });
      setStep("redirecting");
      window.location.assign(onboard.url);
    } catch (err) {
      setSubmitting(false);
      const apiErr = err as ApiError;
      if (apiErr.status === 401) {
        const returnTo = encodeURIComponent("/become-a-creator");
        router.replace(`/sign-in?returnTo=${returnTo}`);
        return;
      }
      setError(apiErr.message || "Could not start onboarding.");
    }
  }

  if (step === "verifying") {
    return (
      <section className="mx-auto max-w-xl px-4 py-16 md:px-0">
        <Card>
          <CardHeader>
            <CardTitle>Verifying payouts setup</CardTitle>
            <CardDescription>{statusMsg ?? "One moment…"}</CardDescription>
          </CardHeader>
          <CardContent>
            {statusOk === null ? (
              <div className="flex items-center gap-3 text-sm text-fg-muted">
                <Spinner className="size-4" />
                <span>Checking your account…</span>
              </div>
            ) : statusOk ? (
              <Alert>
                <AlertTitle>You're set up</AlertTitle>
                <AlertDescription>
                  Head to your dashboard to publish your first skill.
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="destructive">
                <AlertTitle>Finish payouts setup</AlertTitle>
                <AlertDescription>{statusMsg}</AlertDescription>
              </Alert>
            )}
          </CardContent>
          <CardFooter className="flex justify-end gap-2">
            <Button asChild variant="ghost">
              <Link href="/dashboard">Go to dashboard</Link>
            </Button>
            {!statusOk ? (
              <Button onClick={() => setStep("form")}>Try again</Button>
            ) : null}
          </CardFooter>
        </Card>
      </section>
    );
  }

  if (step === "redirecting") {
    return (
      <section className="mx-auto flex max-w-xl flex-col items-center px-4 py-24 md:px-0">
        <Spinner className="size-8" />
        <p className="mt-6 text-sm text-fg-muted">
          Redirecting you to Stripe…
        </p>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-xl px-4 py-16 md:px-0">
      <span className="tag-label mb-3 block">CREATORS</span>
      <h1
        className="mb-2"
        style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", fontWeight: 900, letterSpacing: "-0.04em", lineHeight: 0.95 }}
      >
        BECOME A<br />CREATOR.
      </h1>
      <p className="mt-4 text-lg" style={{ color: "var(--color-fg-muted)" }}>
        Pick your handle, set your payout country, and we'll send you to Stripe
        to finish payouts setup.
      </p>

      <Card className="mt-8" style={{ border: "none", boxShadow: "0 4px 32px rgba(10,10,10,0.08)", borderRadius: "1rem" }}>
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle>Your creator profile</CardTitle>
            <CardDescription>
              You can edit display details later — handle and country are
              locked once payouts are enabled.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="handle">Handle</Label>
              <Input
                id="handle"
                placeholder="e.g. jane-doe"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                disabled={submitting}
                required
                pattern="[a-z0-9][a-z0-9-]{1,40}[a-z0-9]"
                title="Lowercase letters, numbers, and dashes. 3-42 characters."
              />
              <p className="text-xs text-fg-muted">
                Your public URL will be{" "}
                <code className="font-mono text-xs">
                  skillsgit.com/u/{handle || "your-handle"}
                </code>
                .
              </p>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="country">Payout country</Label>
              <Select
                value={country}
                onValueChange={setCountry}
                disabled={submitting}
              >
                <SelectTrigger id="country">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES.map((c) => (
                    <SelectItem key={c.code} value={c.code}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-start gap-3">
              <Checkbox
                id="terms"
                checked={terms}
                onCheckedChange={(v) => setTerms(v === true)}
                disabled={submitting}
              />
              <Label htmlFor="terms" className="text-sm leading-relaxed">
                I agree to the{" "}
                <Link href="/legal/creator-terms" className="underline">
                  creator terms
                </Link>{" "}
                and understand that Stripe will collect tax and identity
                information needed for payouts.
              </Label>
            </div>
            {error ? (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <Spinner className="size-4" />
                  Setting up…
                </>
              ) : (
                "Continue to Stripe"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </section>
  );
}

export default function BecomeACreatorPage() {
  return (
    <Suspense fallback={null}>
      <BecomeCreatorInner />
    </Suspense>
  );
}
