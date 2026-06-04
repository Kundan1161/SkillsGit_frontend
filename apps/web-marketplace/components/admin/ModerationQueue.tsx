"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ModerationQueueItem } from "@/lib/api/admin";

export function ModerationQueue({ items }: { items: ModerationQueueItem[] }) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-fg-muted">
        Queue is empty — nothing pending review.
      </p>
    );
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Skill</TableHead>
          <TableHead>Creator</TableHead>
          <TableHead>Version</TableHead>
          <TableHead>Submitted</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="w-1" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((it) => (
          <TableRow key={it.skill_id}>
            <TableCell className="font-medium">{it.name}</TableCell>
            <TableCell>
              {it.creator_handle ? `@${it.creator_handle}` : "—"}
            </TableCell>
            <TableCell>{it.submitted_version ?? "—"}</TableCell>
            <TableCell className="text-xs text-fg-muted">
              {it.submitted_at
                ? new Date(it.submitted_at).toLocaleString()
                : "—"}
            </TableCell>
            <TableCell>
              <Badge variant="warning">{it.status}</Badge>
            </TableCell>
            <TableCell>
              <Button asChild variant="outline" size="sm">
                <Link href={`/admin/skills/${it.skill_id}/review`}>
                  Review
                </Link>
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
