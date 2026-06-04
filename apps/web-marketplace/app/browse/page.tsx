import type { Metadata } from "next";

import { SearchBar } from "@/components/discovery/SearchBar";
import { FilterSidebar } from "@/components/discovery/FilterSidebar";
import { SortDropdown } from "@/components/discovery/SortDropdown";
import { SkillGrid } from "@/components/discovery/SkillGrid";
import { EmptyState } from "@/components/discovery/EmptyState";
import {
  catalogApi,
  type CatalogQuery,
  type CatalogSort,
} from "@/lib/api/catalog";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Browse skills",
  description: "Browse every skill on Skills Marketplace by category, price, AI model, and more.",
};

function searchParamsToQuery(
  sp: Record<string, string | string[] | undefined>,
): CatalogQuery {
  const csv = (v: string | string[] | undefined) =>
    typeof v === "string" && v ? v.split(",").filter(Boolean) : undefined;
  return {
    q: typeof sp.q === "string" ? sp.q : undefined,
    categories: csv(sp.categories),
    pricing_models: csv(sp.pricing_models),
    required_models: csv(sp.required_models),
    tags: csv(sp.tags),
    min_rating:
      typeof sp.min_rating === "string"
        ? Number(sp.min_rating) || undefined
        : undefined,
    sort: typeof sp.sort === "string" ? (sp.sort as CatalogSort) : undefined,
    limit: 24,
    cursor: typeof sp.cursor === "string" ? sp.cursor : undefined,
  };
}

export default async function BrowsePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const query = searchParamsToQuery(sp);
  const [page, categories] = await Promise.all([
    catalogApi.listSkillsSafe(query),
    catalogApi.listCategories(),
  ]);

  const heading = query.q ? `Results for "${query.q}"` : "Browse all skills";

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 md:px-8">
      <header className="mb-10">
        <span className="tag-label mb-3 block">BROWSE</span>
        <h1
          className="mb-6"
          style={{ fontSize: "clamp(2rem, 5vw, 4rem)", fontWeight: 900, letterSpacing: "-0.04em", lineHeight: 0.95 }}
        >
          {heading}
        </h1>
        <div className="max-w-xl">
          <SearchBar redirectTo="browse" defaultValue={query.q} />
        </div>
      </header>
      <div className="flex flex-col gap-10 lg:flex-row">
        <FilterSidebar categories={categories.items} />
        <div className="flex-1 space-y-6">
          <div className="flex items-center justify-between">
            <p className="tag-label">{page.items.length} {page.items.length === 1 ? "SKILL" : "SKILLS"}{page.page.has_more ? "+" : ""}</p>
            <SortDropdown initial={query.sort ?? "relevance"} />
          </div>
          {page.items.length === 0 ? <EmptyState /> : <SkillGrid skills={page.items} />}
        </div>
      </div>
    </div>
  );
}
