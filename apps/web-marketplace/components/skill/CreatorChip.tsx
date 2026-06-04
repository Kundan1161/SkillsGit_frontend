import Link from "next/link";
import { BadgeCheck } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { CreatorChip as CreatorChipData } from "@/lib/api/catalog";
import { cn } from "@/lib/utils";

export interface CreatorChipProps {
  creator: CreatorChipData;
  size?: "sm" | "md";
  className?: string;
}

export function CreatorChip({
  creator,
  size = "sm",
  className,
}: CreatorChipProps) {
  const initials = (creator.display_name ?? creator.handle)
    .slice(0, 2)
    .toUpperCase();
  return (
    <Link
      href={`/u/${creator.handle}`}
      className={cn(
        "inline-flex items-center gap-2 rounded-full px-1.5 py-1 text-sm hover:bg-bg-muted",
        className,
      )}
    >
      <Avatar className={size === "md" ? "h-7 w-7" : "h-5 w-5"}>
        {creator.avatar_url ? (
          <AvatarImage src={creator.avatar_url} alt="" />
        ) : null}
        <AvatarFallback className="text-[10px]">{initials}</AvatarFallback>
      </Avatar>
      <span className="font-medium">
        {creator.display_name ?? `@${creator.handle}`}
      </span>
      {creator.is_verified ? (
        <BadgeCheck className="h-4 w-4 text-brand-500" aria-label="Verified creator" />
      ) : null}
    </Link>
  );
}
