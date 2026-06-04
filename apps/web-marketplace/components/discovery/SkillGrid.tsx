import { SkillCard } from "./SkillCard";
import type { SkillCardItem } from "@/lib/api/catalog";

export interface SkillGridProps {
  skills: SkillCardItem[];
  emptyMessage?: string;
}

export function SkillGrid({ skills, emptyMessage }: SkillGridProps) {
  if (skills.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-bg-muted/50 px-6 py-16 text-center">
        <p className="text-sm text-fg-muted">
          {emptyMessage ?? "No skills match these filters."}
        </p>
      </div>
    );
  }
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {skills.map((s) => (
        <SkillCard key={s.id} skill={s} />
      ))}
    </div>
  );
}
