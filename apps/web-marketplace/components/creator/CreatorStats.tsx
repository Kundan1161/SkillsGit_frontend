import { Layers, ShoppingBag, Star } from "lucide-react";

import type { CreatorStats } from "@/lib/api/catalog";

export interface CreatorStatsStripProps {
  stats: CreatorStats;
}

export function CreatorStatsStrip({ stats }: CreatorStatsStripProps) {
  const showSales = stats.total_sales >= 100;
  return (
    <dl className="grid grid-cols-2 gap-3 md:grid-cols-3">
      <StatTile
        icon={<Layers className="h-4 w-4" />}
        label="Skills"
        value={stats.total_skills.toLocaleString()}
      />
      {showSales ? (
        <StatTile
          icon={<ShoppingBag className="h-4 w-4" />}
          label="Total sales"
          value={stats.total_sales.toLocaleString()}
        />
      ) : null}
      {stats.rating_avg != null ? (
        <StatTile
          icon={<Star className="h-4 w-4 fill-rating text-rating" />}
          label="Avg rating"
          value={stats.rating_avg.toFixed(1)}
        />
      ) : null}
    </dl>
  );
}

function StatTile({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-border bg-bg-raised p-4">
      <dt className="flex items-center gap-2 text-xs text-fg-subtle">
        {icon}
        <span>{label}</span>
      </dt>
      <dd className="mt-1 text-2xl font-semibold tracking-tight">{value}</dd>
    </div>
  );
}
