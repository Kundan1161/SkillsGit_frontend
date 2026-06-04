"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { LicenseRead } from "@/lib/api/delivery";

const STATUS_LABEL: Record<string, string> = {
  active: "Active",
  expired: "Expired",
  revoked: "Revoked",
};

const SOURCE_LABEL: Record<string, string> = {
  one_time: "Owned",
  subscription: "Subscribed",
  free: "Free",
  freemium: "Free",
  grant: "Granted",
};

export function LicenseCard({ license }: { license: LicenseRead }) {
  return (
    <Card className="flex flex-col gap-3 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold tracking-tight">
            {license.skill.name}
          </h3>
          <p className="text-xs text-fg-muted">
            {license.skill.creator_handle
              ? `@${license.skill.creator_handle}`
              : "Unknown creator"}
          </p>
        </div>
        <Badge variant="secondary">{SOURCE_LABEL[license.source] ?? license.source}</Badge>
      </div>

      <div className="flex items-center justify-between text-xs text-fg-muted">
        <span>
          Status:{" "}
          <span className="text-fg">{STATUS_LABEL[license.status] ?? license.status}</span>
        </span>
        {license.current_version ? (
          <span>v{license.current_version.version}</span>
        ) : (
          <span>No version</span>
        )}
      </div>

      <div className="mt-auto flex justify-end">
        <Button asChild variant="primary" size="sm">
          <Link href={`/library/${license.id}`}>Open</Link>
        </Button>
      </div>
    </Card>
  );
}
