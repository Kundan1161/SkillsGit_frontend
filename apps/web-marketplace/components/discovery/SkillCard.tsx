import Link from "next/link";
import { Star } from "lucide-react";
import { categoryLabel, formatPrice, type SkillCardItem } from "@/lib/api/catalog";
import { cn } from "@/lib/utils";
import { TiltCard } from "@/components/ui/tilt-card";

const ACCENTS = [
  { fg: "#7c3aed", bg: "rgba(124,58,237,0.1)" },
  { fg: "#3b82f6", bg: "rgba(59,130,246,0.1)" },
  { fg: "#10b981", bg: "rgba(16,185,129,0.1)" },
  { fg: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
  { fg: "#f43f5e", bg: "rgba(244,63,94,0.1)" },
  { fg: "#06b6d4", bg: "rgba(6,182,212,0.1)" },
];

function getAccent(slug: string) {
  const idx = slug.split("").reduce((a, c) => a + c.charCodeAt(0), 0) % ACCENTS.length;
  return ACCENTS[idx] ?? ACCENTS[0]!;
}

export function SkillCard({ skill, className }: { skill: SkillCardItem; className?: string }) {
  const href = `/s/${skill.creator.handle}/${skill.slug}`;
  const accent = getAccent(skill.slug);

  return (
    <TiltCard className={cn("neu-skill-card group relative flex h-full flex-col overflow-hidden", className)} intensity={8} scale={1.02}>
    <article className="contents">
      {/* Cover — inset neumorphic well */}
      <div
        className="relative mx-3 mt-3 flex aspect-[16/9] items-center justify-center overflow-hidden"
        style={{
          borderRadius: "1.125rem",
          boxShadow: "var(--shadow-neu-inset-sm)",
          background: accent.bg,
        }}
      >
        {skill.cover_image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={skill.cover_image_url}
            alt=""
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            style={{ borderRadius: "1.125rem" }}
          />
        ) : (
          <span
            className="select-none font-black opacity-25"
            style={{ fontSize: "clamp(2rem,5vw,4rem)", color: accent.fg, letterSpacing: "-0.04em" }}
          >
            {skill.name.slice(0, 2).toUpperCase()}
          </span>
        )}

        {/* Category pill — floated bottom-left, neumorphic */}
        {skill.category && (
          <div
            className="absolute bottom-2.5 left-2.5 px-3 py-1"
            style={{
              background: "var(--color-bg)",
              boxShadow: "3px 3px 8px rgba(166,162,153,0.4), -2px -2px 6px rgba(255,255,255,0.8)",
              borderRadius: "9999px",
            }}
          >
            <span className="tag-label" style={{ color: accent.fg }}>
              {categoryLabel(skill.category)}
            </span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="flex flex-1 flex-col p-5">
        {/* Stars */}
        {skill.rating_avg != null && skill.rating_count > 0 && (
          <div className="mb-2 flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((i) => (
              <Star
                key={i}
                className="h-3 w-3"
                style={{
                  fill: i <= Math.round(skill.rating_avg ?? 0) ? "#f59e0b" : "transparent",
                  color: "#f59e0b",
                }}
              />
            ))}
            <span className="ml-1.5 text-[11px] font-bold" style={{ color: "var(--color-fg-muted)" }}>
              {(skill.rating_avg ?? 0).toFixed(1)}
            </span>
          </div>
        )}

        {/* Title */}
        <h3
          className="mb-1.5 font-bold leading-snug"
          style={{ fontSize: "0.9rem", letterSpacing: "-0.01em" }}
        >
          <Link
            href={href}
            className="after:absolute after:inset-0 after:content-[''] transition-colors hover:text-brand-500"
          >
            {skill.name}
          </Link>
        </h3>

        {skill.tagline && (
          <p className="mb-4 line-clamp-2 text-xs leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>
            {skill.tagline}
          </p>
        )}

        {/* Footer */}
        <div className="mt-auto flex items-center justify-between">
          {/* Creator avatar */}
          <div className="flex items-center gap-2">
            <div
              className="flex h-6 w-6 shrink-0 items-center justify-center text-[10px] font-black text-white"
              style={{
                background: accent.fg,
                boxShadow: "2px 2px 6px rgba(166,162,153,0.4),-1px -1px 4px rgba(255,255,255,0.7)",
                borderRadius: "50%",
              }}
            >
              {skill.creator.handle.slice(0, 1).toUpperCase()}
            </div>
            <span className="truncate text-[11px]" style={{ color: "var(--color-fg-subtle)" }}>
              @{skill.creator.handle}
            </span>
          </div>

          {/* Price — inset neumorphic pill */}
          <div
            className="px-3 py-1.5"
            style={{
              background: "var(--color-bg)",
              boxShadow: "var(--shadow-neu-inset-sm)",
              borderRadius: "9999px",
            }}
          >
            <span className="text-sm font-black" style={{ color: "#059669", letterSpacing: "-0.01em" }}>
              {formatPrice(skill)}
            </span>
          </div>
        </div>
      </div>
    </article>
    </TiltCard>
  );
}
