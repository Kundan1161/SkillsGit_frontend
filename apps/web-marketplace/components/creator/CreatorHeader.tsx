import { BadgeCheck, ExternalLink } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { categoryLabel, type CreatorProfilePublic } from "@/lib/api/catalog";

export interface CreatorHeaderProps {
  creator: CreatorProfilePublic;
}

export function CreatorHeader({ creator }: CreatorHeaderProps) {
  const initials = (creator.display_name ?? creator.handle)
    .slice(0, 2)
    .toUpperCase();
  return (
    <header className="flex flex-col items-start gap-6 md:flex-row md:items-center">
      <Avatar className="h-24 w-24 border border-border">
        {creator.avatar_url ? (
          <AvatarImage src={creator.avatar_url} alt="" />
        ) : null}
        <AvatarFallback className="text-2xl">{initials}</AvatarFallback>
      </Avatar>
      <div className="flex-1 space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {creator.display_name ?? `@${creator.handle}`}
          </h1>
          {creator.is_verified ? (
            <BadgeCheck className="h-5 w-5 text-brand-500" aria-label="Verified creator" />
          ) : null}
        </div>
        <p className="text-sm text-fg-muted">@{creator.handle}</p>

        {creator.bio_md ? (
          <p className="max-w-prose whitespace-pre-wrap text-sm text-fg-muted">
            {creator.bio_md}
          </p>
        ) : null}

        <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-fg-subtle">
          {creator.website_url ? (
            <a
              href={creator.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 hover:text-fg"
            >
              <ExternalLink className="h-3 w-3" /> Website
            </a>
          ) : null}
          {Object.entries(creator.social ?? {}).map(([k, v]) => (
            <a
              key={k}
              href={v}
              target="_blank"
              rel="noopener noreferrer"
              className="capitalize hover:text-fg"
            >
              {k}
            </a>
          ))}
        </div>

        {creator.industries.length > 0 ? (
          <div className="flex flex-wrap gap-1.5 pt-2">
            {creator.industries.map((ind) => (
              <Badge key={ind} variant="outline">
                {categoryLabel(ind) || ind}
              </Badge>
            ))}
          </div>
        ) : null}
      </div>
    </header>
  );
}
