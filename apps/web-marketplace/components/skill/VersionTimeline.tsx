import { Ban } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { VersionItem } from "@/lib/api/catalog";

export interface VersionTimelineProps {
  versions: VersionItem[];
}

export function VersionTimeline({ versions }: VersionTimelineProps) {
  if (versions.length === 0) {
    return (
      <p className="text-sm text-fg-muted">No versions published yet.</p>
    );
  }
  return (
    <ol className="relative space-y-6 border-l border-border pl-6">
      {versions.map((v, idx) => (
        <li key={v.id} className="relative">
          <span
            className={cn(
              "absolute -left-[31px] top-1 inline-flex h-3 w-3 rounded-full",
              v.is_yanked ? "bg-fg-subtle" : idx === 0 ? "bg-brand-500" : "bg-border",
            )}
            aria-hidden="true"
          />
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "font-mono text-sm font-medium",
                v.is_yanked && "text-fg-subtle line-through",
              )}
            >
              v{v.version}
            </span>
            {idx === 0 && !v.is_yanked ? (
              <Badge variant="default" className="text-[10px]">
                Latest
              </Badge>
            ) : null}
            {v.is_yanked ? (
              <Badge
                variant="outline"
                className="text-[10px]"
                title={v.yank_reason ?? "Yanked"}
              >
                <Ban className="mr-1 h-3 w-3" /> Yanked
              </Badge>
            ) : null}
            {v.released_at ? (
              <span className="text-xs text-fg-subtle">
                {new Date(v.released_at).toLocaleDateString()}
              </span>
            ) : null}
          </div>
          {v.changelog_md ? (
            <pre 
              className="mt-2 whitespace-pre-wrap p-4 font-sans text-xs leading-relaxed text-fg border-none"
              style={{
                borderRadius: "1rem",
                background: "var(--color-bg)",
                boxShadow: "var(--shadow-neu-inset-sm)",
              }}
            >
              {v.changelog_md}
            </pre>
          ) : null}
        </li>
      ))}
    </ol>
  );
}
