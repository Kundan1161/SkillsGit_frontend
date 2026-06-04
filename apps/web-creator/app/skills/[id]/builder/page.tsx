"use client";

import Link from "next/link";
import { use } from "react";
import {
  CheckCircle2,
  Eye,
  PlayCircle,
  Rocket,
  Settings2,
} from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { GraphCanvas } from "@/components/builder/graph-canvas";
import { NodePalette } from "@/components/builder/node-palette";
import { NodeInspector } from "@/components/builder/node-inspector";

/**
 * Builder route. Server-rendered chrome, client-rendered canvas.
 *
 * Layout note: the three-column flex collapses to a single column
 * with the canvas dominating on small screens. We keep the palette
 * and inspector hidden under `md:` to avoid a cramped mobile shell;
 * the canvas is the most useful surface on any size.
 */
export default function BuilderPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <div className="flex h-screen flex-col bg-bg">
      <SiteHeader />

      {/* Top action bar */}
      <div className="flex items-center gap-3 border-b border-border bg-bg-raised px-4 py-2 md:px-6">
        <div className="flex min-w-0 items-center gap-2">
          <p className="truncate text-sm font-medium text-fg">
            Untitled skill
          </p>
          <Badge variant="outline" className="font-mono text-[10px]">
            v0.1.0
          </Badge>
          <span className="text-xs text-fg-subtle">· draft {id}</span>
        </div>
        <div className="ml-auto flex items-center gap-1">
          <Button asChild variant="ghost" size="sm">
            <Link href={`/skills/${id}/config`}>
              <Settings2 className="h-4 w-4" />
              Config
            </Link>
          </Button>
          <Button asChild variant="ghost" size="sm">
            <Link href={`/skills/${id}/preview`}>
              <Eye className="h-4 w-4" />
              Preview
            </Link>
          </Button>
          <Button asChild variant="ghost" size="sm">
            <Link href={`/skills/${id}/sandbox`}>
              <PlayCircle className="h-4 w-4" />
              Sandbox
            </Link>
          </Button>
          <Separator orientation="vertical" className="mx-1 h-6" />
          <Button asChild size="sm">
            <Link href={`/skills/${id}/publish`}>
              <Rocket className="h-4 w-4" />
              Publish
            </Link>
          </Button>
        </div>
      </div>

      {/* Builder body — three-column on md+, canvas-only below */}
      <div className="flex min-h-0 flex-1">
        <div className="hidden md:block">
          <NodePalette />
        </div>
        <div className="min-w-0 flex-1">
          <GraphCanvas />
        </div>
        <div className="hidden lg:block">
          <NodeInspector />
        </div>
      </div>

      {/* Bottom status bar */}
      <div className="flex items-center gap-3 border-t border-border bg-bg-raised px-4 py-1.5 text-xs text-fg-muted md:px-6">
        <Badge variant="success" className="gap-1">
          <CheckCircle2 className="h-3 w-3" />
          Valid
        </Badge>
        <span className="text-fg-subtle">·</span>
        <span>Saved 2s ago</span>
        <span className="text-fg-subtle">·</span>
        <span>0 nodes · 0 edges</span>
        <span className="ml-auto font-mono text-[10px] text-fg-subtle">
          Phase 0 stub — compilation arrives in Phase 3
        </span>
      </div>
    </div>
  );
}
