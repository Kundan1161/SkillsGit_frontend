import type { Metadata } from "next";

import { SearchBar } from "@/components/discovery/SearchBar";
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
  title: "Search",
  description: "Search for skills, tags, or creators.",
  robots: { index: false },
};

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const q = typeof sp.q === "string" ? sp.q : "";
  const sort = typeof sp.sort === "string" ? (sp.sort as CatalogSort) : "relevance";

  const query: CatalogQuery = {
    q: q || undefined,
    sort,
    limit: 24,
  };

  const page = q ? await catalogApi.listSkillsSafe(query) : { items: [], page: { has_more: false, limit: 24, next_cursor: null } };

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 md:px-8">
      <header className="mb-10 space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
          {q ? `Results for "${q}"` : "Search skills"}
        </h1>
        <SearchBar redirectTo="search" defaultValue={q} />
      </header>

      {q ? (
        <>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-fg-muted">
              {page.items.length} results
            </p>
            <SortDropdown initial={sort} />
          </div>
          {page.items.length === 0 ? (
            <EmptyState
              title={`No results for "${q}"`}
              description="Try a different keyword or browse popular categories below."
            />
          ) : (
            <SkillGrid skills={page.items} />
          )}
        </>
      ) : (
        <EmptyState
          title="Search the marketplace"
          description="Type a keyword above — try 'dcf', 'design critique', or 'social media'."
        />
      )}
    </div>
  );
}
