"use client";

import { GripVertical } from "lucide-react";
import { cn } from "@/lib/utils";
import { NODE_KIND_META } from "@/lib/builder/store";

/**
 * Left-rail palette of draggable node kinds. In Phase 0 the chips
 * are visually present and use the HTML5 drag-start to set a
 * payload, but the canvas does NOT yet implement the drop handler.
 *
 * Real drag-to-create + sub-graph templates land in Phase 3.
 */
export function NodePalette() {
  function onDragStart(
    event: React.DragEvent<HTMLDivElement>,
    kind: string,
  ) {
    event.dataTransfer.setData("application/skillsgit-node", kind);
    event.dataTransfer.effectAllowed = "move";
  }

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-bg-raised">
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
          Nodes
        </h2>
      </header>
      <div className="flex-1 overflow-y-auto p-3">
        <ul className="space-y-1.5">
          {NODE_KIND_META.map((meta) => (
            <li key={meta.kind}>
              <div
                role="button"
                tabIndex={0}
                draggable
                onDragStart={(e) => onDragStart(e, meta.kind)}
                className={cn(
                  "group flex cursor-grab items-start gap-2 rounded-md border border-border bg-bg p-2.5 text-left transition-colors hover:border-brand-500/60 hover:bg-bg-muted active:cursor-grabbing focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500",
                  "ring-1 ring-inset ring-transparent",
                  meta.accent,
                )}
              >
                <GripVertical
                  className="mt-0.5 h-3.5 w-3.5 shrink-0 text-fg-subtle"
                  aria-hidden
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-fg">{meta.label}</p>
                  <p className="mt-0.5 text-xs leading-snug text-fg-muted">
                    {meta.description}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>

        <div className="mt-6 rounded-md border border-dashed border-border p-3 text-xs text-fg-subtle">
          <p className="font-medium text-fg-muted">Sub-graph templates</p>
          <p className="mt-1">
            Drop-in starter flows arrive in Phase 3 — pick from the
            <a
              href="/templates"
              className="ml-1 text-brand-500 underline-offset-2 hover:underline"
            >
              templates gallery
            </a>{" "}
            for now.
          </p>
        </div>
      </div>
    </aside>
  );
}
