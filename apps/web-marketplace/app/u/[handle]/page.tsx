import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { CreatorHeader } from "@/components/creator/CreatorHeader";
import { CreatorStatsStrip } from "@/components/creator/CreatorStats";
import { CreatorSkillsGrid } from "@/components/creator/CreatorSkillsGrid";
import { catalogApi } from "@/lib/api/catalog";

export const revalidate = 60;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ handle: string }>;
}): Promise<Metadata> {
  const { handle } = await params;
  const creator = await catalogApi.getCreator(handle);
  if (!creator) return { title: "Creator not found" };
  const name = creator.display_name ?? `@${creator.handle}`;
  return {
    title: `${name}`,
    description: `Skills by ${name} on Skills Marketplace.`,
    alternates: { canonical: `/u/${creator.handle}` },
    openGraph: {
      title: name,
      description: creator.bio_md?.slice(0, 150),
      type: "profile",
      images: creator.avatar_url ? [{ url: creator.avatar_url }] : undefined,
    },
  };
}

export default async function CreatorProfilePage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const creator = await catalogApi.getCreator(handle);
  if (!creator) notFound();

  const skills = await catalogApi
    .listCreatorSkills(handle, { sort: "most_sold", limit: 24 })
    .catch(() => ({ items: [], page: { has_more: false, limit: 24, next_cursor: null } }));

  return (
    <div className="mx-auto max-w-7xl space-y-10 px-4 py-12 md:px-8">
      <CreatorHeader creator={creator} />
      <CreatorStatsStrip stats={creator.stats} />
      <section>
        <h2 className="mb-4 text-xl font-semibold">Skills</h2>
        <CreatorSkillsGrid skills={skills.items} />
      </section>
    </div>
  );
}
