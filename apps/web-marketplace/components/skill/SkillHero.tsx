import Link from "next/link";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { CreatorChip } from "./CreatorChip";
import { categoryLabel, type SkillDetail } from "@/lib/api/catalog";

export interface SkillHeroProps {
  skill: SkillDetail;
}

export function SkillHero({ skill }: SkillHeroProps) {
  return (
    <div className="space-y-4">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/browse">Browse</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          {skill.category ? (
            <>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href={`/c/${skill.category}`}>
                    {categoryLabel(skill.category)}
                  </Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
            </>
          ) : null}
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{skill.name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
        {skill.name}
      </h1>
      {skill.tagline ? (
        <p className="text-lg text-fg-muted">{skill.tagline}</p>
      ) : null}
      <div>
        <CreatorChip creator={skill.creator} size="md" />
      </div>
      {skill.cover_image_url ? (
        <div
          className="aspect-[16/9] w-full overflow-hidden border-none"
          style={{ 
            backgroundImage: `url(${skill.cover_image_url})`,
            borderRadius: "1.5rem",
            backgroundSize: "cover",
            backgroundPosition: "center",
            boxShadow: "var(--shadow-neu-md)"
          }}
          aria-label={`${skill.name} cover image`}
          role="img"
        />
      ) : (
        <div 
          className="flex aspect-[16/9] w-full items-center justify-center text-lg md:text-xl font-black text-fg-muted tracking-tight border-none"
          style={{
            borderRadius: "1.5rem",
            background: "var(--color-bg)",
            boxShadow: "var(--shadow-neu-inset)",
          }}
        >
          {skill.name}
        </div>
      )}
      {skill.screenshots.length > 0 ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {skill.screenshots.map((src) => (
            <div
              key={src}
              className="aspect-[4/3] overflow-hidden bg-cover bg-center border-none"
              style={{ 
                backgroundImage: `url(${src})`,
                borderRadius: "0.85rem",
                boxShadow: "var(--shadow-neu-sm)"
              }}
              role="presentation"
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
