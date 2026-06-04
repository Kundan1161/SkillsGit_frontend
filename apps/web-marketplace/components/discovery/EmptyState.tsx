import Link from "next/link";
import { Search } from "lucide-react";


export interface EmptyStateProps {
  title?: string;
  description?: string;
  suggestions?: { label: string; href: string }[];
}

export function EmptyState({
  title = "No skills match these filters",
  description = "Try removing a filter or broadening your search.",
  suggestions = [
    { label: "Finance", href: "/c/finance" },
    { label: "Design", href: "/c/design" },
    { label: "Engineering", href: "/c/engineering" },
    { label: "Marketing", href: "/c/marketing" },
  ],
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div
        className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl"
        style={{ background: "rgba(124,58,237,0.08)" }}
      >
        <Search className="h-7 w-7" style={{ color: "#7c3aed" }} />
      </div>
      <h2 className="text-lg font-bold" style={{ letterSpacing: "-0.02em" }}>{title}</h2>
      <p className="mt-2 text-sm" style={{ color: "var(--color-fg-muted)" }}>{description}</p>
      {suggestions.length > 0 && (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
          <span className="tag-label mr-1">Popular:</span>
          {suggestions.map((s) => (
            <Link
              key={s.href}
              href={s.href}
              className="rounded-full px-4 py-1.5 text-xs font-semibold transition-all hover:-translate-y-0.5"
              style={{ background: "rgba(124,58,237,0.08)", color: "#7c3aed" }}
            >
              {s.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
