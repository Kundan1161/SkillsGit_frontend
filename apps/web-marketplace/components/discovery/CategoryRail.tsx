import Link from "next/link";
import {
  BarChart3,
  Brush,
  Code2,
  HeadphonesIcon,
  Heart,
  Megaphone,
  Microscope,
  PencilRuler,
  Scale,
  Settings2,
  Sparkles,
  TrendingUp,
  Wallet,
} from "lucide-react";

import { categoryLabel, type CategoryItem } from "@/lib/api/catalog";
import { cn } from "@/lib/utils";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  finance: Wallet,
  design: PencilRuler,
  data: BarChart3,
  marketing: Megaphone,
  sales: TrendingUp,
  legal: Scale,
  operations: Settings2,
  engineering: Code2,
  "customer-support": HeadphonesIcon,
  productivity: Sparkles,
  creative: Brush,
  research: Microscope,
  other: Heart,
};

export interface CategoryRailProps {
  categories: CategoryItem[];
  className?: string;
}

export function CategoryRail({ categories, className }: CategoryRailProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6",
        className,
      )}
    >
      {categories.map((c) => {
        const Icon = ICON_MAP[c.slug] ?? Sparkles;
        return (
          <Link
            key={c.slug}
            href={`/c/${c.slug}`}
            className="neu-tile group flex flex-col items-start gap-3 p-5"
          >
            <span
              className="inline-flex h-10 w-10 items-center justify-center"
              style={{
                background: "var(--color-bg)",
                boxShadow: "var(--shadow-neu-sm)",
                borderRadius: "0.875rem",
              }}
            >
              <Icon className="h-5 w-5" style={{ color: "#7c3aed" }} />
            </span>
            <div>
              <p className="text-sm font-bold" style={{ letterSpacing: "-0.01em" }}>
                {categoryLabel(c.slug) || c.name}
              </p>
              <p className="text-xs" style={{ color: "var(--color-fg-subtle)" }}>{c.skill_count} skills</p>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
