"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useTransition } from "react";
import { X } from "lucide-react";
import { categoryLabel, type CategoryItem } from "@/lib/api/catalog";

const PRICING_OPTIONS = [
  { value: "free",         label: "Free" },
  { value: "one_time",     label: "One-time" },
  { value: "subscription", label: "Subscription" },
  { value: "freemium",     label: "Freemium" },
];

const RATING_OPTIONS = [
  { value: "3",   label: "3★ & up" },
  { value: "4",   label: "4★ & up" },
  { value: "4.5", label: "4.5★ & up" },
];

export interface FilterSidebarProps {
  categories: CategoryItem[];
}

export function FilterSidebar({ categories }: FilterSidebarProps) {
  const router    = useRouter();
  const params    = useSearchParams();
  const pathname  = usePathname();
  const [, go]    = useTransition();

  const readCsv = (key: string) =>
    (params.get(key) ?? "").split(",").filter(Boolean);

  const push = (next: URLSearchParams) => {
    next.delete("cursor");
    go(() => router.push(`${pathname}?${next.toString()}`));
  };

  const toggleCsv = (key: string, value: string) => {
    const next = new URLSearchParams(params.toString());
    const cur  = readCsv(key);
    const upd  = cur.includes(value) ? cur.filter(v => v !== value) : [...cur, value];
    upd.length === 0 ? next.delete(key) : next.set(key, upd.join(","));
    push(next);
  };

  const setScalar = (key: string, value: string | null) => {
    const next = new URLSearchParams(params.toString());
    value === null ? next.delete(key) : next.set(key, value);
    push(next);
  };

  const clearAll = () => {
    const next = new URLSearchParams();
    const q = params.get("q");
    if (q) next.set("q", q);
    go(() => router.push(`${pathname}?${next.toString()}`));
  };

  const activeCats    = readCsv("categories");
  const activePricing = readCsv("pricing_models");
  const activeRating  = params.get("min_rating") ?? "";
  const anyActive     = activeCats.length > 0 || activePricing.length > 0 || activeRating;

  return (
    <aside
      aria-label="Filters"
      className="sticky top-24 hidden h-fit w-60 shrink-0 lg:block"
    >
      {/* Neumorphic panel */}
      <div
        style={{
          background: "var(--color-bg)",
          boxShadow: "var(--shadow-neu-md)",
          borderRadius: "1.5rem",
          padding: "1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="font-black" style={{ fontSize: "0.9rem", letterSpacing: "-0.02em", color: "var(--color-fg)" }}>
            FILTERS
          </h2>
          {anyActive && (
            <button
              onClick={clearAll}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold transition-all"
              style={{
                background: "var(--color-bg)",
                boxShadow: "var(--shadow-neu-sm)",
                borderRadius: "9999px",
                color: "#7c3aed",
                border: "none",
                cursor: "pointer",
              }}
            >
              <X className="h-3 w-3" />
              Clear
            </button>
          )}
        </div>

        {/* Category */}
        <FilterGroup label="CATEGORY">
          <div className="flex flex-col gap-2">
            {categories.map((c) => {
              const active = activeCats.includes(c.slug);
              return (
                <button
                  key={c.slug}
                  onClick={() => toggleCsv("categories", c.slug)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "8px 12px",
                    borderRadius: "0.75rem",
                    border: "none",
                    cursor: "pointer",
                    background: "var(--color-bg)",
                    boxShadow: active
                      ? "var(--shadow-neu-inset-sm)"
                      : "var(--shadow-neu-xs)",
                    transition: "box-shadow 0.2s ease",
                    width: "100%",
                  }}
                >
                  <span style={{ fontSize: "0.8rem", fontWeight: active ? 700 : 500, color: active ? "#7c3aed" : "var(--color-fg-muted)", textAlign: "left" }}>
                    {categoryLabel(c.slug) || c.name}
                  </span>
                  <span style={{ fontSize: "0.65rem", fontWeight: 700, color: active ? "#7c3aed" : "var(--color-fg-subtle)", letterSpacing: "0.05em" }}>
                    {c.skill_count}
                  </span>
                </button>
              );
            })}
          </div>
        </FilterGroup>

        {/* Pricing */}
        <FilterGroup label="PRICING">
          <div className="flex flex-wrap gap-2">
            {PRICING_OPTIONS.map((o) => {
              const active = activePricing.includes(o.value);
              return (
                <button
                  key={o.value}
                  onClick={() => toggleCsv("pricing_models", o.value)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "9999px",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    letterSpacing: "0.02em",
                    background: "var(--color-bg)",
                    boxShadow: active ? "var(--shadow-neu-inset-sm)" : "var(--shadow-neu-xs)",
                    color: active ? "#7c3aed" : "var(--color-fg-muted)",
                    transition: "all 0.2s ease",
                  }}
                >
                  {o.label}
                </button>
              );
            })}
          </div>
        </FilterGroup>

        {/* Rating */}
        <FilterGroup label="MIN RATING">
          <div className="flex flex-col gap-2">
            {RATING_OPTIONS.map((o) => {
              const active = activeRating === o.value;
              return (
                <button
                  key={o.value}
                  onClick={() => setScalar("min_rating", active ? null : o.value)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "8px 12px",
                    borderRadius: "0.75rem",
                    border: "none",
                    cursor: "pointer",
                    background: "var(--color-bg)",
                    boxShadow: active ? "var(--shadow-neu-inset-sm)" : "var(--shadow-neu-xs)",
                    color: active ? "#7c3aed" : "var(--color-fg-muted)",
                    fontSize: "0.8rem",
                    fontWeight: active ? 700 : 500,
                    transition: "all 0.2s ease",
                    width: "100%",
                    textAlign: "left",
                  }}
                >
                  {o.label}
                </button>
              );
            })}
          </div>
        </FilterGroup>
      </div>
    </aside>
  );
}

function FilterGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3">
      <span className="tag-label" style={{ fontSize: "0.58rem" }}>{label}</span>
      {children}
    </div>
  );
}
