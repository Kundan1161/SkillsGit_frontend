import type { Metadata } from "next";
import Link from "next/link";
import {
  BarChart3, Brush, Code2, HeadphonesIcon, Heart, Megaphone,
  Microscope, PencilRuler, Scale, Settings2, Sparkles, TrendingUp, Wallet,
} from "lucide-react";
import { catalogApi, categoryLabel } from "@/lib/api/catalog";

export const metadata: Metadata = {
  title: "All categories",
  description: "Browse all skill categories on SkillsGit.",
};

export const revalidate = 300;

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  finance:           Wallet,
  design:            PencilRuler,
  data:              BarChart3,
  marketing:         Megaphone,
  sales:             TrendingUp,
  legal:             Scale,
  operations:        Settings2,
  engineering:       Code2,
  "customer-support": HeadphonesIcon,
  productivity:      Sparkles,
  creative:          Brush,
  research:          Microscope,
  other:             Heart,
};

const ACCENTS = [
  "#7c3aed","#3b82f6","#10b981","#f59e0b",
  "#f43f5e","#06b6d4","#8b5cf6","#ec4899",
  "#14b8a6","#f97316","#6366f1","#84cc16",
];

function getAccent(slug: string) {
  return ACCENTS[slug.split("").reduce((a,c)=>a+c.charCodeAt(0),0) % ACCENTS.length]!;
}

export default async function AllCategoriesPage() {
  const categories = await catalogApi.listCategories().catch(() => ({ items: [] }));

  return (
    <div style={{ background: "var(--color-bg)", minHeight: "100vh" }}>
      {/* ── Header ── */}
      <div className="mx-auto max-w-7xl px-6 pt-16 pb-12 lg:px-16">
        <span className="tag-label mb-4 block">CATEGORIES</span>
        <h1
          style={{
            fontSize: "clamp(3rem,7vw,6rem)",
            fontWeight: 900,
            letterSpacing: "-0.045em",
            lineHeight: 0.88,
            color: "var(--color-fg)",
          }}
        >
          ALL<br />
          <span style={{
            background: "linear-gradient(135deg,#7c3aed,#6366f1)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}>
            CATEGORIES.
          </span>
        </h1>
        <p className="mt-5 max-w-md text-lg leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>
          {categories.items.length} professional domains.
          Every expert. Every skill.
        </p>
      </div>

      {/* ── Grid ── */}
      <div className="mx-auto max-w-7xl px-6 pb-24 lg:px-16">
        {categories.items.length === 0 ? (
          <div className="flex flex-col items-center py-32 text-center">
            <div
              className="mb-6 flex h-20 w-20 items-center justify-center"
              style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-md)", borderRadius: "1.5rem" }}
            >
              <Sparkles className="h-9 w-9" style={{ color: "#7c3aed" }} />
            </div>
            <p className="text-xl font-black" style={{ letterSpacing: "-0.03em", color: "var(--color-fg)" }}>No categories yet</p>
            <p className="mt-2 text-base" style={{ color: "var(--color-fg-muted)" }}>Check back soon.</p>
          </div>
        ) : (
          <div className="scroll-stagger grid grid-cols-1 gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {categories.items.map((cat) => {
              const Icon = ICON_MAP[cat.slug] ?? Sparkles;
              const accent = getAccent(cat.slug);
              return (
                <Link
                  key={cat.slug}
                  href={`/c/${cat.slug}`}
                  className="scroll-reveal-scale neu-tile group flex flex-col gap-5 p-6"
                >
                  {/* Icon in neumorphic raised square */}
                  <div
                    style={{
                      width: 52, height: 52,
                      background: "var(--color-bg)",
                      boxShadow: "var(--shadow-neu-sm)",
                      borderRadius: "1rem",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      transition: "box-shadow 0.3s ease",
                    }}
                  >
                    <Icon className="h-6 w-6" style={{ color: accent }} />
                  </div>

                  <div className="flex-1">
                    <p className="font-black" style={{ fontSize: "1rem", letterSpacing: "-0.02em", color: "var(--color-fg)" }}>
                      {categoryLabel(cat.slug) || cat.name}
                    </p>
                    <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>
                      {cat.skill_count} {cat.skill_count === 1 ? "skill" : "skills"}
                    </p>
                  </div>

                  {/* Accent underline — grows on hover, neumorphic inset feel */}
                  <div style={{ height: 3, borderRadius: "9999px", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset-sm)", overflow: "hidden" }}>
                    <div
                      style={{
                        height: "100%",
                        width: "0%",
                        background: accent,
                        borderRadius: "9999px",
                        transition: "width 0.4s cubic-bezier(0.16,1,0.3,1)",
                      }}
                      className="group-hover:!w-full"
                    />
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
