"use client";

import { useEffect, useState } from "react";

import { ModerationQueue } from "@/components/admin/ModerationQueue";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  adminApi,
  type AdminUserSummary,
  type ModerationQueueItem,
} from "@/lib/api/admin";

export default function AdminHomePage() {
  const [queue, setQueue] = useState<ModerationQueueItem[] | null>(null);
  const [users, setUsers] = useState<AdminUserSummary[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const q = await adminApi.moderationQueue();
        if (!cancelled) setQueue(q.items);
      } catch (e) {
        if (!cancelled)
          setErr((e as { message?: string }).message ?? "Forbidden");
      }
      try {
        const u = await adminApi.listUsers();
        if (!cancelled) setUsers(u.items);
      } catch {
        /* admin gating already surfaces err */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (err) {
    return (
      <section className="mx-auto max-w-5xl px-4 py-10 md:px-8">
        <p className="text-danger">{err}</p>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight">Admin</h1>
      <p className="mt-2 text-fg-muted">
        Moderation queue, user management, and recent activity.
      </p>

      <Tabs defaultValue="moderation" className="mt-6">
        <TabsList>
          <TabsTrigger value="moderation">Moderation</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
        </TabsList>

        <TabsContent value="moderation" className="mt-4">
          {queue === null ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <ModerationQueue items={queue} />
          )}
        </TabsContent>

        <TabsContent value="users" className="mt-4">
          {users === null ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <ul className="divide-y divide-border rounded-md border border-border">
              {users.map((u) => (
                <li
                  key={u.id}
                  className="flex items-center justify-between px-4 py-3 text-sm"
                >
                  <div>
                    <span className="font-medium">{u.email}</span>
                    {u.creator_handle ? (
                      <span className="ml-2 text-fg-muted">
                        @{u.creator_handle}
                      </span>
                    ) : null}
                  </div>
                  <div className="flex gap-2 text-xs text-fg-muted">
                    {u.is_admin ? "admin · " : null}
                    {u.is_creator_verified ? "verified · " : null}
                    {u.is_active ? "active" : "suspended"}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </TabsContent>
      </Tabs>
    </section>
  );
}
