"use client";

import { use, useEffect, useState } from "react";

import { SkillReviewPanel } from "@/components/admin/SkillReviewPanel";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { adminApi, type ModerationQueueItem } from "@/lib/api/admin";

export default function AdminSkillReviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [item, setItem] = useState<ModerationQueueItem | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const q = await adminApi.moderationQueue();
        if (cancelled) return;
        const found = q.items.find((i) => i.skill_id === id) ?? null;
        if (found) setItem(found);
        else setErr("Skill is not in the moderation queue.");
      } catch (e) {
        if (!cancelled)
          setErr((e as { message?: string }).message ?? "Failed to load");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (err) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <p className="text-danger">{err}</p>
      </section>
    );
  }
  if (item === null) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="mt-4 h-40 w-full" />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">{item.name}</h1>
        <p className="mt-1 text-sm text-fg-muted">
          by {item.creator_handle ? `@${item.creator_handle}` : "unknown"} · v
          {item.submitted_version}
          <Badge variant="warning" className="ml-3">
            {item.status}
          </Badge>
        </p>
      </header>

      {item.rejection_reason ? (
        <div className="mt-6 rounded-md border border-warning/40 bg-warning/10 p-4 text-sm">
          <strong>Previous rejection reason:</strong> {item.rejection_reason}
        </div>
      ) : null}

      <div className="mt-8 rounded-md border border-border p-4 text-sm text-fg-muted">
        Full markdown body preview lands in Phase 2 — see
        <code className="mx-1">05-trust-and-quality.md</code>.
      </div>

      <div className="mt-8">
        <SkillReviewPanel
          skillId={id}
          onActed={() => {
            window.location.href = "/admin";
          }}
        />
      </div>
    </section>
  );
}
