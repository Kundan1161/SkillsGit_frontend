"use client";

import { Badge } from "@/components/ui/badge";

interface VersionRow {
  id: string;
  version: string;
  released_at: string | null;
  is_yanked: boolean;
}

interface Props {
  versions: VersionRow[];
  currentVersion: string | null;
}

export function VersionPicker({ versions, currentVersion }: Props) {
  if (versions.length === 0) {
    return (
      <p className="text-sm text-fg-muted">
        No released versions yet for this skill.
      </p>
    );
  }
  return (
    <ul className="divide-y divide-border rounded-md border border-border">
      {versions.map((v) => (
        <li
          key={v.id}
          className="flex items-center justify-between px-4 py-3 text-sm"
        >
          <div>
            <span className="font-medium">v{v.version}</span>
            {v.released_at ? (
              <span className="ml-2 text-fg-muted">
                released {new Date(v.released_at).toLocaleDateString()}
              </span>
            ) : (
              <span className="ml-2 text-fg-muted">draft</span>
            )}
          </div>
          <div className="flex gap-2">
            {v.is_yanked ? <Badge variant="danger">Yanked</Badge> : null}
            {v.version === currentVersion ? (
              <Badge variant="default">Current</Badge>
            ) : null}
          </div>
        </li>
      ))}
    </ul>
  );
}
