import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import { Brain, ChevronRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { personasApi } from "@/lib/api/occupations";
import { formatPrice } from "@/lib/api/catalog";

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
  const persona = await personasApi.getByHandle(handle, slug);
  if (!persona) return { title: "Persona not found" };
  return {
    title: `${persona.name} — Expert Persona`,
    description: (persona.tagline ?? persona.creator_intro_md ?? "").slice(0, 150),
  };
}

export default async function PersonaDetailPage({
  params,
}: {
  params: Promise<PageParams>;
}) {
  const { handle, slug } = await params;
  const persona = await personasApi.getByHandle(handle, slug);
  if (!persona) notFound();

  const priceLabel = formatPrice({
    pricing_model: persona.pricing.model as "free" | "one_time" | "subscription" | "freemium",
    one_time_price_cents: persona.pricing.one_time_price_cents,
    subscription_price_cents: persona.pricing.subscription_price_cents,
  });

  const parentOcc = persona.parent_occupation;

  return (
    <article className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      {/* Breadcrumb */}
      <nav className="mb-6 flex items-center gap-1.5 text-xs text-fg-subtle">
        <Link
          href={`/occupations/${parentOcc.creator_handle}/${parentOcc.slug}`}
          className="hover:text-fg hover:underline"
        >
          {parentOcc.name}
        </Link>
        <ChevronRight className="h-3 w-3" />
        <span className="text-fg">{persona.name}</span>
      </nav>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12">
        {/* Left */}
        <div className="space-y-8 lg:col-span-8">
          {/* Hero */}
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">Persona overlay</Badge>
              {persona.specialization && (
                <Badge variant="outline">{persona.specialization}</Badge>
              )}
            </div>

            <div className="flex items-start gap-4">
              {persona.cover_image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={persona.cover_image_url}
                  alt=""
                  className="h-16 w-16 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-brand-500/10 text-brand-500">
                  <Brain className="h-8 w-8" />
                </div>
              )}
              <div>
                <h1 className="text-3xl font-semibold tracking-tight">
                  {persona.name}
                </h1>
                {persona.tagline && (
                  <p className="mt-1 text-lg text-fg-muted">{persona.tagline}</p>
                )}
                <p className="mt-1 text-sm text-fg-subtle">
                  by{" "}
                  <Link
                    href={`/u/${persona.creator.handle}`}
                    className="font-medium text-fg hover:underline"
                  >
                    {persona.creator.display_name ?? `@${persona.creator.handle}`}
                  </Link>
                  {persona.years_of_experience != null && (
                    <> · {persona.years_of_experience} years of experience</>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Creator intro */}
          {persona.creator_intro_md && (
            <div>
              <h2 className="mb-3 text-base font-semibold">About this persona</h2>
              <pre className="whitespace-pre-wrap rounded-md border border-border bg-bg-muted/50 p-4 font-sans text-sm leading-relaxed text-fg">
                {persona.creator_intro_md}
              </pre>
            </div>
          )}

          {/* Neurons */}
          <div>
            <h2 className="mb-4 text-base font-semibold">
              Memory neurons ({persona.neuron_count})
            </h2>
            <p className="mb-4 text-sm text-fg-muted">
              Each neuron is a real experience this expert lived through —
              a situation, what they decided, and what happened. Every answer
              from this persona cites the neurons it consulted.
            </p>
            {persona.neurons.length > 0 ? (
              <div className="divide-y divide-border rounded-lg border border-border">
                {persona.neurons.map((n) => (
                  <div key={n.id} className="px-4 py-3">
                    <p className="text-sm font-medium text-fg">{n.name}</p>
                    {n.tagline && (
                      <p className="mt-0.5 text-xs text-fg-subtle">{n.tagline}</p>
                    )}
                    {n.vault_path && (
                      <p className="mt-1 font-mono text-[10px] text-fg-subtle">
                        {n.vault_path}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-fg-muted">
                Neurons are private to license holders.
              </p>
            )}
          </div>
        </div>

        {/* Right — sticky sidebar */}
        <aside className="lg:col-span-4">
          <div className="sticky top-20 space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  <span className="text-2xl font-bold text-price">
                    {priceLabel}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link
                  href={`/checkout?persona=${persona.id}`}
                  className="block w-full rounded-md bg-brand-500 px-4 py-2.5 text-center text-sm font-medium text-white hover:bg-brand-600"
                >
                  Buy persona overlay
                </Link>
                <p className="text-center text-xs text-fg-subtle">
                  Requires an active{" "}
                  <Link
                    href={`/occupations/${parentOcc.creator_handle}/${parentOcc.slug}`}
                    className="underline hover:text-fg"
                  >
                    {parentOcc.name}
                  </Link>{" "}
                  license.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick facts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <Row label="Neurons" value={persona.neuron_count} />
                {persona.years_of_experience != null && (
                  <Row
                    label="Experience"
                    value={`${persona.years_of_experience} yrs`}
                  />
                )}
                {persona.stats.total_sales >= 25 && (
                  <Row
                    label="Sales"
                    value={persona.stats.total_sales.toLocaleString()}
                  />
                )}
                <Row
                  label="Parent occupation"
                  value={
                    <Link
                      href={`/occupations/${parentOcc.creator_handle}/${parentOcc.slug}`}
                      className="hover:underline"
                    >
                      {parentOcc.name}
                    </Link>
                  }
                />
              </CardContent>
            </Card>
          </div>
        </aside>
      </div>

      {/* Mobile sticky bottom bar */}
      <div className="fixed inset-x-0 bottom-0 z-30 flex items-center justify-between gap-3 border-t border-border bg-bg-raised p-3 shadow-lg lg:hidden">
        <div>
          <p className="text-xs text-fg-subtle">Price</p>
          <p className="text-base font-semibold text-price">{priceLabel}</p>
        </div>
        <Link
          href={`/checkout?persona=${persona.id}`}
          className="rounded-md bg-brand-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-600"
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
