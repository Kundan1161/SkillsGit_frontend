import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import { Star } from "lucide-react";

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SkillHero } from "@/components/skill/SkillHero";
import { PriceCard } from "@/components/skill/PriceCard";
import { AiRequirementsCard } from "@/components/skill/AiRequirementsCard";
import { VersionTimeline } from "@/components/skill/VersionTimeline";
import { WhatsInsidePreview } from "@/components/skill/WhatsInsidePreview";
import { InspiredBySection } from "@/components/skill/InspiredBySection";
import { FaqAccordion } from "@/components/skill/FaqAccordion";
import {
  catalogApi,
  categoryLabel,
  formatPrice,
} from "@/lib/api/catalog";

export const revalidate = 60;

interface PageParams {
  handle: string;
  slug: string;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<PageParams>;
}): Promise<Metadata> {
  const { handle, slug } = await params;
  const skill = await catalogApi.getSkillByHandle(handle, slug);
  if (!skill) {
    return { title: "Skill not found" };
  }
  const title = `${skill.name} by ${skill.creator.display_name ?? "@" + skill.creator.handle}`;
  const description = (skill.tagline ?? "").slice(0, 150);
  const isUnlisted = skill.status === "unlisted";
  return {
    title,
    description,
    alternates: {
      canonical: `/s/${skill.creator.handle}/${skill.slug}`,
    },
    robots: isUnlisted ? { index: false, follow: false } : undefined,
    openGraph: {
      title,
      description,
      type: "website",
      images: skill.cover_image_url ? [{ url: skill.cover_image_url }] : undefined,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: skill.cover_image_url ? [skill.cover_image_url] : undefined,
    },
  };
}

export default async function SkillDetailPage({
  params,
}: {
  params: Promise<PageParams>;
}) {
  const { handle, slug } = await params;
  const [skill, versionsRes] = await Promise.all([
    catalogApi.getSkillByHandle(handle, slug),
    // We need the skill id before listing versions, so do it conditionally.
    (async () => null)(),
  ]);

  if (!skill) {
    notFound();
  }

  const versions = await catalogApi
    .listVersions(skill.id)
    .catch(() => ({ items: [], page: { has_more: false, limit: 20, next_cursor: null } }));

  // JSON-LD Product schema.
  const offers = {
    "@type": "Offer",
    priceCurrency: skill.pricing.currency,
    price: (() => {
      const cents =
        skill.pricing.model === "subscription"
          ? skill.pricing.subscription_price_cents ?? 0
          : skill.pricing.one_time_price_cents ?? 0;
      return (cents / 100).toFixed(2);
    })(),
    availability: "https://schema.org/InStock",
    url: `/s/${skill.creator.handle}/${skill.slug}`,
  };
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: skill.name,
    description: skill.tagline ?? undefined,
    image: skill.cover_image_url ?? undefined,
    brand: {
      "@type": "Brand",
      name: skill.creator.display_name ?? `@${skill.creator.handle}`,
    },
    offers,
  };
  if (skill.stats.rating_count > 0 && skill.stats.rating_avg != null) {
    jsonLd.aggregateRating = {
      "@type": "AggregateRating",
      ratingValue: skill.stats.rating_avg,
      reviewCount: skill.stats.rating_count,
    };
  }

  return (
    <article className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <script
        type="application/ld+json"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12">
        {/* Left column */}
        <div className="space-y-8 lg:col-span-8">
          <SkillHero skill={skill} />

          <Tabs defaultValue="overview">
            <TabsList 
              className="flex flex-wrap h-auto gap-1 border-none p-1.5 w-fit"
              style={{
                background: "var(--color-bg)",
                boxShadow: "var(--shadow-neu-inset-sm)",
                borderRadius: "1rem",
              }}
            >
              {[
                { value: "overview", label: "Overview" },
                { value: "inside", label: "What's inside" },
                { value: "inspired", label: "Inspired by" },
                { value: "versions", label: `Versions (${versions.items.length})` },
                { value: "reviews", label: `Reviews (${skill.stats.rating_count})` },
                { value: "faq", label: "FAQ" }
              ].map((tab) => (
                <TabsTrigger
                  key={tab.value}
                  value={tab.value}
                  className="px-4 py-2 text-xs md:text-sm font-bold transition-all duration-200 border-none rounded-lg text-fg-muted data-[state=active]:bg-bg data-[state=active]:shadow-[var(--shadow-neu-sm)] data-[state=active]:text-brand-500"
                  style={{ borderRadius: "0.75rem" }}
                >
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              {skill.description_md ? (
                <pre 
                  className="whitespace-pre-wrap p-5 font-sans text-sm leading-relaxed text-fg border-none"
                  style={{
                    borderRadius: "1.25rem",
                    background: "var(--color-bg)",
                    boxShadow: "var(--shadow-neu-inset-sm)",
                  }}
                >
                  {skill.description_md}
                </pre>
              ) : (
                <p className="text-sm text-fg-muted">
                  This creator hasn&apos;t added a long description yet.
                </p>
              )}

              {skill.tags.length > 0 ? (
                <div className="mt-6 flex flex-wrap gap-2">
                  {skill.tags.map((t) => (
                    <Link
                      key={t}
                      href={`/browse?tags=${encodeURIComponent(t)}`}
                      className="inline-flex"
                    >
                      <Badge variant="outline">{t}</Badge>
                    </Link>
                  ))}
                </div>
              ) : null}
            </TabsContent>

            <TabsContent value="inside" className="mt-6">
              <WhatsInsidePreview bodyMd={skill.preview_body_md} />
            </TabsContent>

            <TabsContent value="inspired" className="mt-6">
              <InspiredBySection urls={skill.inspired_by_urls} />
            </TabsContent>

            <TabsContent value="versions" className="mt-6">
              <VersionTimeline versions={versions.items} />
            </TabsContent>

            <TabsContent value="reviews" className="mt-6">
              <Card className="border-none" style={{ borderRadius: "1.25rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-md)" }}>
                <CardHeader>
                  <CardTitle className="text-base">
                    {skill.stats.rating_count > 0 ? (
                      <span className="flex items-center gap-2">
                        <Star className="h-4 w-4 fill-rating text-rating" />
                        {(skill.stats.rating_avg ?? 0).toFixed(1)} from{" "}
                        {skill.stats.rating_count} reviews
                      </span>
                    ) : (
                      "No reviews yet"
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-fg-muted">
                    Reviews launch in Phase 2. Owners of an active license will
                    be able to leave a rating and short writeup here.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="faq" className="mt-6">
              <FaqAccordion faqMd={skill.faq_md} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Right column — sticky */}
        <aside className="space-y-4 lg:col-span-4">
          <div className="sticky top-20 space-y-4">
            <PriceCard skill={skill} />
            <AiRequirementsCard ai={skill.ai_requirements} />
            <Card className="border-none" style={{ borderRadius: "1.25rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-md)" }}>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick facts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {skill.category ? (
                  <Row
                    label="Category"
                    value={
                      <Link
                        href={`/c/${skill.category}`}
                        className="hover:underline"
                      >
                        {categoryLabel(skill.category)}
                      </Link>
                    }
                  />
                ) : null}
                {skill.latest_version ? (
                  <Row
                    label="Latest version"
                    value={`v${skill.latest_version.version}`}
                  />
                ) : null}
                {skill.stats.total_sales >= 25 ? (
                  <Row
                    label="Total sales"
                    value={skill.stats.total_sales.toLocaleString()}
                  />
                ) : null}
                {skill.stats.rating_count > 0 ? (
                  <Row
                    label="Rating"
                    value={`${skill.stats.rating_avg?.toFixed(1) ?? "—"} (${skill.stats.rating_count})`}
                  />
                ) : null}
                <Row
                  label="Pricing"
                  value={formatPrice({
                    pricing_model: skill.pricing.model,
                    one_time_price_cents: skill.pricing.one_time_price_cents,
                    subscription_price_cents: skill.pricing.subscription_price_cents,
                  })}
                />
              </CardContent>
            </Card>
          </div>
        </aside>
      </div>

      {/* Mobile sticky bottom bar */}
      <div
        className="fixed inset-x-0 bottom-0 z-30 flex items-center justify-between gap-3 p-3 lg:hidden"
        style={{ background: "var(--color-bg)", boxShadow: "0 -8px 24px rgba(166,162,153,0.45)" }}
      >
        <div>
          <p className="text-xs text-fg-subtle">Price</p>
          <p className="text-base font-semibold text-price">
            {formatPrice({
              pricing_model: skill.pricing.model,
              one_time_price_cents: skill.pricing.one_time_price_cents,
              subscription_price_cents: skill.pricing.subscription_price_cents,
            })}
          </p>
        </div>
        <Link
          href={`/checkout?skill=${skill.id}`}
          className="neu-btn-brand px-5 py-2.5 text-sm font-bold text-white"
          style={{ borderRadius: "0.85rem" }}
        >
          Buy now
        </Link>
      </div>
    </article>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-xs text-fg-subtle">{label}</dt>
      <dd className="text-right text-sm text-fg">{value}</dd>
    </div>
  );
}
