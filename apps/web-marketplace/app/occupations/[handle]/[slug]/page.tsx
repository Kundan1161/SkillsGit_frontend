import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Link from "next/link";
import { BookOpen, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { occupationsApi, personasApi } from "@/lib/api/occupations";
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
  const occ = await occupationsApi.getByHandle(handle, slug);
  if (!occ) return { title: "Occupation not found" };
  return {
    title: `${occ.name} — AI Occupation`,
    description: (occ.tagline ?? occ.summary_md ?? "").slice(0, 150),
  };
}

export default async function OccupationDetailPage({
  params,
}: {
  params: Promise<PageParams>;
}) {
  const { handle, slug } = await params;
  const [occ, personas] = await Promise.all([
    occupationsApi.getByHandle(handle, slug),
    (async () => [])(), // filled after we have the id
  ]);

  if (!occ) notFound();

  const overlayPersonas = await personasApi.listForOccupation(occ.id);

  // Group members by domain
  const byDomain = occ.members.reduce<
    Record<string, typeof occ.members>
  >((acc, m) => {
    const d = m.domain || "General";
    (acc[d] ??= []).push(m);
    return acc;
  }, {});
  const domains = Object.keys(byDomain).sort();

  const priceLabel = formatPrice({
    pricing_model: occ.pricing.model as "free" | "one_time" | "subscription" | "freemium",
    one_time_price_cents: occ.pricing.one_time_price_cents,
    subscription_price_cents: occ.pricing.subscription_price_cents,
  });

  return (
    <article className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12">
        {/* Left */}
        <div className="space-y-8 lg:col-span-8">
          {/* Hero */}
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">Occupation</Badge>
              {occ.latest_version && (
                <Badge variant="outline" className="font-mono text-xs">
                  v{occ.latest_version}
                </Badge>
              )}
            </div>
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
              {occ.name}
            </h1>
            {occ.tagline && (
              <p className="text-lg text-fg-muted">{occ.tagline}</p>
            )}
            <p className="text-sm text-fg-subtle">
              by{" "}
              <Link
                href={`/u/${occ.creator.handle}`}
                className="font-medium text-fg hover:underline"
              >
                {occ.creator.display_name ?? `@${occ.creator.handle}`}
              </Link>
            </p>
          </div>

          <Tabs defaultValue="skills">
            <TabsList>
              <TabsTrigger value="skills">
                Skills ({occ.members.length})
              </TabsTrigger>
              <TabsTrigger value="personas">
                Personas ({overlayPersonas.length})
              </TabsTrigger>
              <TabsTrigger value="about">About</TabsTrigger>
            </TabsList>

            {/* Skills tab — grouped by domain */}
            <TabsContent value="skills" className="mt-6 space-y-8">
              {domains.map((domain) => (
                <div key={domain}>
                  <h3 className="mb-3 text-sm font-semibold uppercase tracking-widest text-fg-subtle">
                    {domain}
                  </h3>
                  <div className="divide-y divide-border rounded-lg border border-border">
                    {(byDomain[domain] ?? []).map((m) => (
                      <div
                        key={m.id}
                        className="flex items-center justify-between gap-4 px-4 py-3"
                      >
                        <div className="min-w-0">
                          <Link
                            href={`/s/${m.skill.creator_handle}/${m.skill.slug}`}
                            className="text-sm font-medium text-fg hover:underline"
                          >
                            {m.skill.name}
                          </Link>
                          {m.skill.tagline && (
                            <p className="truncate text-xs text-fg-subtle">
                              {m.skill.tagline}
                            </p>
                          )}
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          {m.pinned && (
                            <Badge variant="secondary" className="text-[10px]">
                              pinned
                            </Badge>
                          )}
                          <Badge
                            variant={
                              m.role === "core" ? "default" : "outline"
                            }
                            className="text-[10px]"
                          >
                            {m.role}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              {occ.members.length === 0 && (
                <p className="text-sm text-fg-muted">
                  No skills added to this occupation yet.
                </p>
              )}
            </TabsContent>

            {/* Personas tab */}
            <TabsContent value="personas" className="mt-6">
              {overlayPersonas.length === 0 ? (
                <p className="text-sm text-fg-muted">
                  No persona overlays published yet.
                </p>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {overlayPersonas.map((p) => (
                    <Link
                      key={p.id}
                      href={`/personas/${p.creator.handle}/${p.slug}`}
                      className="group rounded-xl border border-border bg-bg-raised p-5 transition-colors hover:border-brand-500"
                    >
                      <div className="flex items-start gap-3">
                        {p.cover_image_url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={p.cover_image_url}
                            alt=""
                            className="h-10 w-10 rounded-full object-cover"
                          />
                        ) : (
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-500/10 text-brand-500">
                            <Users className="h-5 w-5" />
                          </div>
                        )}
                        <div className="min-w-0">
                          <p className="font-medium text-fg group-hover:text-brand-500">
                            {p.name}
                          </p>
                          {p.tagline && (
                            <p className="mt-0.5 truncate text-xs text-fg-muted">
                              {p.tagline}
                            </p>
                          )}
                          <p className="mt-1 text-xs text-fg-subtle">
                            {p.neuron_count} neurons ·{" "}
                            {formatPrice({
                              pricing_model: p.pricing.model as "free" | "one_time" | "subscription" | "freemium",
                              one_time_price_cents: p.pricing.one_time_price_cents,
                              subscription_price_cents: p.pricing.subscription_price_cents,
                            })}
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* About tab */}
            <TabsContent value="about" className="mt-6">
              {occ.summary_md ? (
                <pre className="whitespace-pre-wrap rounded-md border border-border bg-bg-muted/50 p-4 font-sans text-sm leading-relaxed text-fg">
                  {occ.summary_md}
                </pre>
              ) : (
                <p className="text-sm text-fg-muted">No description yet.</p>
              )}
            </TabsContent>
          </Tabs>
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
                  href={`/checkout?occupation=${occ.id}`}
                  className="block w-full rounded-md bg-brand-500 px-4 py-2.5 text-center text-sm font-medium text-white hover:bg-brand-600"
                >
                  Buy occupation vault
                </Link>
                <p className="text-center text-xs text-fg-subtle">
                  Includes all {occ.members.length} skills. Persona overlays
                  sold separately.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick facts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <Row label="Skills" value={occ.members.length} />
                <Row label="Persona overlays" value={overlayPersonas.length} />
                {occ.latest_version && (
                  <Row label="Version" value={`v${occ.latest_version}`} />
                )}
                {occ.domains.length > 0 && (
                  <Row label="Domains" value={occ.domains.join(", ")} />
                )}
                {occ.stats.total_sales >= 25 && (
                  <Row
                    label="Sales"
                    value={occ.stats.total_sales.toLocaleString()}
                  />
                )}
              </CardContent>
            </Card>

            {overlayPersonas.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-sm font-medium text-fg-muted">
                    <BookOpen className="h-4 w-4" />
                    Add a persona overlay
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-fg-subtle">
                    Persona overlays add a practitioner's real-world experience
                    on top of this occupation vault. Requires an active
                    occupation license.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </aside>
      </div>
    </article>
  );
}

function Row({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-xs text-fg-subtle">{label}</dt>
      <dd className="text-right text-sm text-fg">{value}</dd>
    </div>
  );
}
