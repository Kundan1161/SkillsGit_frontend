"use client";

import { MousePointerSquareDashed } from "lucide-react";
import { useSelectedNode } from "@/lib/builder/store";
import { Badge } from "@/components/ui/badge";

/**
 * Right rail. When no node is selected we show a placeholder; when one is
 * selected we show a placeholder form. Real per-kind forms (RHF + Zod)
 * arrive in Phase 3 per `skill-creator/01-visual-builder.md` § Inspector.
 */
export function NodeInspector() {
  const selected = useSelectedNode();

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border bg-bg-raised">
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
          Inspector
        </h2>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        {selected ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-[10px]">
                {selected.data.kind}
              </Badge>
              <p className="truncate text-sm font-medium text-fg">
                {selected.id}
              </p>
            </div>
            <p className="text-xs text-fg-muted">
              A typed form for this node lands in Phase 3. The shape is
              defined in <code className="font-mono">lib/builder/types.ts</code>.
            </p>
            <div className="space-y-2">
              <div className="h-9 rounded-md bg-bg-muted" />
              <div className="h-24 rounded-md bg-bg-muted" />
              <div className="h-9 rounded-md bg-bg-muted" />
            </div>
          </div>
        ) : (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <MousePointerSquareDashed
              className="mb-3 h-8 w-8 text-fg-subtle"
              aria-hidden
            />
            <p className="text-sm font-medium text-fg">Select a node</p>
            <p className="mt-1 max-w-[14rem] text-xs text-fg-muted">
              Click any node on the canvas to edit its data here.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
