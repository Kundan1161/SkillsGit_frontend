"use client";

import { useEffect, useState } from "react";

import { LicenseCard } from "@/components/library/LicenseCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { deliveryApi, type LicenseRead, type LicenseSource } from "@/lib/api/delivery";

type FilterKey = "all" | "one_time" | "free" | "subscription" | "expired";

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "subscription", label: "Subscribed" },
  { key: "one_time", label: "One-time" },
  { key: "free", label: "Free" },
  { key: "expired", label: "Expired" },
];

export default function LibraryPage() {
  const [items, setItems] = useState<LicenseRead[] | null>(null);
  const [filter, setFilter] = useState<FilterKey>("all");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const params: { source?: LicenseSource } = {};
        if (filter === "one_time") params.source = "one_time";
        else if (filter === "free") params.source = "free";
        else if (filter === "subscription") params.source = "subscription";
        const res = await deliveryApi.listMyLicenses(params);
        if (cancelled) return;
        let filtered = res.items;
        if (filter === "expired") {
          filtered = res.items.filter((l) => l.status === "expired");
        }
        setItems(filtered);
      } catch (e) {
        const msg = (e as { message?: string }).message ?? "Failed to load library";
        if (!cancelled) setErr(msg);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [filter]);

  return (
    <section className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight">Your library</h1>
      <p className="mt-2 text-fg-muted">Skills you've licensed or claimed.</p>

      <div className="mt-6 flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <Button
            key={f.key}
            size="sm"
            variant={filter === f.key ? "primary" : "outline"}
            onClick={() => setFilter(f.key)}
          >
            {f.label}
          </Button>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items === null && err === null ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-36 w-full" />
          ))
        ) : err ? (
          <p className="text-sm text-danger">{err}</p>
        ) : items && items.length === 0 ? (
          <p className="col-span-full text-sm text-fg-muted">
            No skills here yet. Browse the marketplace to find one.
          </p>
        ) : (
          items?.map((lic) => <LicenseCard key={lic.id} license={lic} />)
        )}
      </div>
    </section>
  );
}
