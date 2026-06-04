import Link from "next/link";
import { cn } from "@/lib/utils";

const TABS: Array<{ slug: string; label: string }> = [
  { slug: "builder", label: "Builder" },
  { slug: "config", label: "Config" },
  { slug: "preview", label: "Preview" },
  { slug: "sandbox", label: "Sandbox" },
  { slug: "publish", label: "Publish" },
  { slug: "versions", label: "Versions" },
];

interface Props {
  skillId: string;
  active: (typeof TABS)[number]["slug"];
}

export function SkillSubnav({ skillId, active }: Props) {
  return (
    <nav className="flex items-center gap-1 border-b border-border bg-bg-raised px-4 md:px-8">
      {TABS.map((tab) => {
        const isActive = tab.slug === active;
        return (
          <Link
            key={tab.slug}
            href={`/skills/${skillId}/${tab.slug}`}
            className={cn(
              "border-b-2 px-3 py-2 text-sm transition-colors",
              isActive
                ? "border-brand-500 text-fg"
                : "border-transparent text-fg-muted hover:text-fg",
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
