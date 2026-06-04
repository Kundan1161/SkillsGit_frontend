"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

import { billing } from "@/lib/api/billing";

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 5000;

function SuccessInner() {
  const params = useSearchParams();
  const router = useRouter();
  const sessionId = params.get("session_id");

  const [status, setStatus] = useState<"processing" | "ready" | "timeout" | "error">(
    "processing",
  );
  const [licenseId, setLicenseId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus("error");
      setErrorMessage("Missing session_id");
      return;
    }
    let cancelled = false;
    const startedAt = Date.now();

    async function poll() {
      try {
        const res = await billing.finalizeCheckoutSession(sessionId!);
        if (cancelled) return;
        if (res.license_id) {
          setLicenseId(res.license_id);
          setStatus("ready");
          // Redirect to library after a short pause so the user sees the
          // confirmation.
          setTimeout(() => {
            if (!cancelled) router.replace(`/library/${res.license_id}`);
          }, 800);
          return;
        }
      } catch {
        // ignore transient errors during polling
      }
      if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
        if (!cancelled) setStatus("timeout");
        return;
      }
      if (!cancelled) {
        setTimeout(poll, POLL_INTERVAL_MS);
      }
    }

    poll();
    return () => {
      cancelled = true;
    };
  }, [sessionId, router]);

  return (
    <section className="mx-auto flex max-w-md flex-col items-center px-4 py-24 md:px-0">
      {status === "processing" ? (
        <>
          <Spinner className="size-8" />
          <h1 className="mt-6 text-2xl font-semibold">Processing your purchase…</h1>
          <p className="mt-2 text-center text-sm text-fg-muted">
            Hang tight — we're confirming with our payments processor. This
            usually takes a couple of seconds.
          </p>
        </>
      ) : null}

      {status === "ready" ? (
        <>
          <h1 className="text-2xl font-semibold">You're all set!</h1>
          <p className="mt-2 text-center text-sm text-fg-muted">
            Taking you to your library…
          </p>
        </>
      ) : null}

      {status === "timeout" ? (
        <Alert className="w-full">
          <AlertTitle>Still processing</AlertTitle>
          <AlertDescription>
            Your purchase went through — we just haven't seen the confirmation
            yet. Check your library in a moment.
          </AlertDescription>
          <div className="mt-4 flex justify-end">
            <Button asChild>
              <Link href="/library">Go to library</Link>
            </Button>
          </div>
        </Alert>
      ) : null}

      {status === "error" ? (
        <Alert variant="destructive" className="w-full">
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>
            {errorMessage ?? "We couldn't confirm your purchase."}
          </AlertDescription>
          <div className="mt-4 flex justify-end">
            <Button asChild>
              <Link href="/browse">Back to browse</Link>
            </Button>
          </div>
        </Alert>
      ) : null}

      {licenseId ? null : null /* keep var referenced for linter */}
    </section>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={null}>
      <SuccessInner />
    </Suspense>
  );
}
