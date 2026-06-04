"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PriceTag } from "@/components/checkout/price-tag";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { billing, type OrderRead } from "@/lib/api/billing";

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function SettingsBillingPage() {
  const [orders, setOrders] = useState<OrderRead[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    billing
      .listMyOrders(50)
      .then((res) => {
        if (!cancelled) {
          setOrders(res.items);
          setLoading(false);
        }
      })
      .catch((err: { message?: string }) => {
        if (!cancelled) {
          setError(err.message ?? "Could not load orders.");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function openPortal() {
    setPortalLoading(true);
    try {
      const res = await billing.openBillingPortal();
      window.location.assign(res.url);
    } catch (err) {
      setPortalLoading(false);
      setError(
        (err as { message?: string })?.message ??
          "Could not open the billing portal.",
      );
    }
  }

  return (
    <section className="mx-auto max-w-4xl px-4 py-12 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight">Billing</h1>
      <p className="mt-2 text-fg-muted">
        Manage your payment methods and review your recent purchases.
      </p>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Payment methods</CardTitle>
          <CardDescription>
            Cards and invoices are managed in your Stripe billing portal.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={openPortal} disabled={portalLoading}>
            {portalLoading ? (
              <>
                <Spinner className="size-4" />
                Opening…
              </>
            ) : (
              "Open Stripe billing portal"
            )}
          </Button>
        </CardContent>
      </Card>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Recent purchases</CardTitle>
          <CardDescription>
            Your one-time skill purchases over the last 90 days.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : error ? (
            <Alert variant="destructive">
              <AlertTitle>Couldn't load orders</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : orders && orders.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Items</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((o) => (
                  <TableRow key={o.id}>
                    <TableCell>{formatDate(o.placed_at)}</TableCell>
                    <TableCell>{o.items.length}</TableCell>
                    <TableCell className="text-right">
                      <PriceTag
                        amountCents={o.subtotal_cents}
                        currency={o.currency}
                      />
                    </TableCell>
                    <TableCell className="capitalize">
                      {o.status.replace(/_/g, " ")}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button asChild variant="ghost" size="sm">
                        <Link href={`/library?order=${o.id}`}>View</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-sm text-fg-muted">No purchases yet.</p>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
