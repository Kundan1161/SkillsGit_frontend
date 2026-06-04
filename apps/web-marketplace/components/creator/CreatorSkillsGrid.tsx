import { SkillGrid } from "@/components/discovery/SkillGrid";
import type { SkillCardItem } from "@/lib/api/catalog";

export interface CreatorSkillsGridProps {
  skills: SkillCardItem[];
}

export function CreatorSkillsGrid({ skills }: CreatorSkillsGridProps) {
  return (
    <SkillGrid
      skills={skills}
      emptyMessage="This creator hasn't published any skills yet."
    />
  );
}
