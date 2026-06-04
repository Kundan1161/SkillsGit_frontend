"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useTransition } from "react";
import { ChevronDown } from "lucide-react";
import type { CatalogSort } from "@/lib/api/catalog";

const OPTIONS: { value: CatalogSort; label: string }[] = [
  { value: "relevance",  label: "Most relevant" },
  { value: "newest",     label: "Newest" },
  { value: "top_rated",  label: "Top rated" },
  { value: "most_sold",  label: "Most sold" },
  { value: "price_asc",  label: "Price: low → high" },
  { value: "price_desc", label: "Price: high → low" },
];

export function SortDropdown({ initial = "relevance" }: { initial?: CatalogSort }) {
  const router   = useRouter();
  const params   = useSearchParams();
  const pathname = usePathname();
  const [, go]   = useTransition();
  const current  = (params.get("sort") as CatalogSort) ?? initial;

  function update(value: string) {
    const next = new URLSearchParams(params.toString());
    value === "relevance" && !next.get("q") ? next.delete("sort") : next.set("sort", value);
    next.delete("cursor");
    go(() => router.push(`${pathname}?${next.toString()}`));
  }

  return (
    <div className="relative inline-flex items-center">
      <select
        value={current}
        onChange={(e) => update(e.target.value)}
        aria-label="Sort by"
        style={{
          appearance: "none",
          WebkitAppearance: "none",
          background: "var(--color-bg)",
          boxShadow: "var(--shadow-neu-sm)",
          borderRadius: "0.875rem",
          border: "none",
          outline: "none",
          padding: "10px 40px 10px 16px",
          fontSize: "0.8rem",
          fontWeight: 700,
          color: "var(--color-fg)",
          cursor: "pointer",
          letterSpacing: "-0.01em",
          fontFamily: "inherit",
          transition: "box-shadow 0.2s ease",
        }}
        onFocus={(e) => {
          (e.target as HTMLSelectElement).style.boxShadow =
            "var(--shadow-neu-inset-sm), 0 0 0 2px rgba(124,58,237,0.25)";
        }}
        onBlur={(e) => {
          (e.target as HTMLSelectElement).style.boxShadow = "var(--shadow-neu-sm)";
        }}
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value} style={{ background: "var(--color-bg)", color: "var(--color-fg)" }}>
            {o.label}
          </option>
        ))}
      </select>
      {/* Neumorphic chevron overlay */}
      <ChevronDown
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5"
        style={{ color: "#7c3aed" }}
      />
    </div>
  );
}
