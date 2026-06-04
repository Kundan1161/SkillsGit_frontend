import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { FilterSidebar } from "@/components/discovery/FilterSidebar";
import { SortDropdown } from "@/components/discovery/SortDropdown";
import { SkillGrid } from "@/components/discovery/SkillGrid";
import { EmptyState } from "@/components/discovery/EmptyState";
import { categoryLabel, catalogApi, type CatalogQuery, type CatalogSort } from "@/lib/api/catalog";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const label = categoryLabel(slug);
  return {
    title: `${label} skills`,
    description: `Browse the best ${label.toLowerCase()} skills on SkillsGit.`,
  };
}

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { slug } = await params;
  const sp = await searchParams;
  const csv = (v: string | string[] | undefined) =>
    typeof v === "string" && v ? v.split(",").filter(Boolean) : undefined;

  const query: CatalogQuery = {
    categories: [slug],
    q: typeof sp.q === "string" ? sp.q : undefined,
    pricing_models: csv(sp.pricing_models),
    required_models: csv(sp.required_models),
    min_rating: typeof sp.min_rating === "string" ? Number(sp.min_rating) || undefined : undefined,
    sort: typeof sp.sort === "string" ? (sp.sort as CatalogSort) : undefined,
    limit: 24,
  };

  const [page, categories] = await Promise.all([
    catalogApi.listSkillsSafe(query),
    catalogApi.listCategories(),
  ]);

  const cat = categories.items.find((c) => c.slug === slug);
  if (!cat && page.items.length === 0 && categories.items.length > 0) notFound();

  const label = cat?.name ?? categoryLabel(slug);

  return (
    <div style={{ background: "var(--color-bg)", minHeight: "100vh" }}>
      {/* ── Header ── */}
      <div className="mx-auto max-w-7xl px-6 pt-14 pb-10 lg:px-16">
        <span className="tag-label mb-4 block">CATEGORY</span>
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1
              style={{
                fontSize: "clamp(2.8rem, 6vw, 5.5rem)",
                fontWeight: 900,
                letterSpacing: "-0.045em",
                lineHeight: 0.9,
                color: "var(--color-fg)",
              }}
            >
              {label.toUpperCase()}
              <span style={{ color: "#7c3aed" }}>.</span>
            </h1>
            <p className="mt-3 text-base leading-relaxed" style={{ color: "var(--color-fg-muted)", maxWidth: "44ch" }}>
              {cat?.description ?? `All ${label.toLowerCase()} skills, curated by practitioners who've been there.`}
            </p>
          </div>
          {/* Count chip */}
          <div
            className="inline-flex shrink-0 flex-col items-center px-6 py-3"
            style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "1rem" }}
          >
            <span style={{ fontSize: "1.8rem", fontWeight: 900, letterSpacing: "-0.04em", background: "linear-gradient(135deg,#7c3aed,#6366f1)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
              {cat?.skill_count ?? page.items.length}
            </span>
            <span className="tag-label">SKILLS</span>
          </div>
        </div>
      </div>

      {/* ── Content ── */}
      <div className="mx-auto max-w-7xl px-6 pb-24 lg:px-16">
        <div className="flex flex-col gap-8 lg:flex-row">
          <FilterSidebar categories={categories.items} />
          <div className="flex-1 space-y-6">
            {/* Toolbar */}
            <div className="flex items-center justify-between">
              <span className="tag-label">
                {page.items.length}{page.page.has_more ? "+" : ""} {page.items.length === 1 ? "SKILL" : "SKILLS"}
              </span>
              <SortDropdown initial={query.sort ?? "most_sold"} />
            </div>
            {page.items.length === 0 ? (
              <EmptyState
                title={`No ${label.toLowerCase()} skills yet`}
                description="Be the first to publish one — or explore other categories."
              />
            ) : (
              <SkillGrid skills={page.items} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
