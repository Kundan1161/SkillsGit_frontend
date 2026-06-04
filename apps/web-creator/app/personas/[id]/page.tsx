"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { Brain, ChevronLeft, Loader2, Rocket } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  personasCreatorApi,
  type NeuronRead,
  type PersonaRead,
} from "@/lib/api/personas";

export default function PersonaDashboardPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [persona, setPersona] = useState<PersonaRead | null>(null);
  const [neurons, setNeurons] = useState<NeuronRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [building, setBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      personasCreatorApi.get(id),
      personasCreatorApi.listNeurons(id),
    ]).then(([p, n]) => {
      setPersona(p);
      setNeurons(n.items);
      setLoading(false);
    });
  }, [id]);

  const handleBuild = async () => {
    setBuilding(true);
    setError(null);
    try {
      await personasCreatorApi.triggerBuild(id);
      setBuilding(false);
    } catch (e) {
      setError((e as { message?: string }).message ?? "Build failed.");
      setBuilding(false);
    }
  };

  const handlePublish = async () => {
    if (!persona) return;
    setPublishing(true);
    setError(null);
    try {
      await personasCreatorApi.publish(id, "1.0.0");
      const updated = await personasCreatorApi.get(id);
      setPersona(updated);
    } catch (e) {
      setError((e as { message?: string }).message ?? "Publish failed.");
    } finally {
      setPublishing(false);
    }
  };

  if (loading || !persona) {
    return (
      <div className="flex min-h-screen flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-8 space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-32 w-full" />
        </main>
      </div>
    );
  }

  const isPublished = persona.status === "published";
  const isDraft = persona.status === "draft";

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-8">
        <div className="mb-6 flex items-center gap-3">
          <Link
            href="/personas"
            className="flex items-center gap-1 text-sm text-fg-muted hover:text-fg"
          >
            <ChevronLeft className="h-4 w-4" />
            Personas
          </Link>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-500/10 text-brand-500">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">
                {persona.name}
              </h1>
              <p className="mt-0.5 text-sm text-fg-muted">
                {persona.parent_occupation_name}
              </p>
            </div>
          </div>
          <Badge
            variant={
              isPublished ? "default" : isDraft ? "outline" : "secondary"
            }
          >
            {persona.status.replace("_", " ")}
          </Badge>
        </div>

        {/* Stats row */}
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Neurons" value={persona.neuron_count} />
          <StatCard
            label="Experience"
            value={
              persona.years_of_experience != null
                ? `${persona.years_of_experience} yrs`
                : "—"
            }
          />
          <StatCard
            label="Specialization"
            value={persona.specialization ?? "—"}
          />
          <StatCard
            label="Last build"
            value={persona.latest_build_id ? "Built" : "Never built"}
          />
        </div>

        {error && (
          <p className="mt-4 text-sm text-danger">{error}</p>
        )}

        {/* Action bar */}
        <div className="mt-6 flex flex-wrap gap-3">
          <Button asChild variant="outline">
            <Link href={`/capture?persona_id=${id}`}>
              Add neuron (capture)
            </Link>
          </Button>
          <Button
            variant="outline"
            onClick={handleBuild}
            disabled={building}
          >
            {building && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {building ? "Building…" : "Build vault"}
          </Button>
          {!isPublished && (
            <Button
              onClick={handlePublish}
              disabled={publishing || persona.neuron_count === 0}
            >
              {publishing ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Rocket className="mr-2 h-4 w-4" />
              )}
              {publishing ? "Publishing…" : "Publish"}
            </Button>
          )}
        </div>
        {!isPublished && persona.neuron_count === 0 && (
          <p className="mt-2 text-xs text-fg-subtle">
            Add at least one neuron before publishing.
          </p>
        )}

        <Separator className="my-8" />

        {/* Neurons list */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">
              Memory neurons ({neurons.length})
            </h2>
            <Link
              href={`/personas/${id}/neurons`}
              className="text-sm text-brand-500 hover:underline"
            >
              Manage order
            </Link>
          </div>

          {neurons.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-12 text-center">
              <p className="text-sm text-fg-muted">No neurons yet.</p>
              <p className="mt-1 text-xs text-fg-subtle">
                Use Capture to add your first memory neuron.
              </p>
              <Button asChild size="sm" className="mt-4">
                <Link href={`/capture`}>Go to Capture</Link>
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-border rounded-xl border border-border">
              {neurons.map((n, i) => (
                <div
                  key={n.id}
                  className="flex items-center gap-4 px-4 py-3"
                >
                  <span className="w-5 shrink-0 text-center text-xs text-fg-subtle">
                    {i + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-fg">
                      {n.name}
                    </p>
                    {n.vault_path && (
                      <p className="font-mono text-[10px] text-fg-subtle">
                        {n.vault_path}
                      </p>
                    )}
                  </div>
                  {n.section && (
                    <Badge variant="outline" className="text-[10px]">
                      {n.section}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="px-4 py-3">
        <p className="text-xs text-fg-subtle">{label}</p>
        <p className="mt-0.5 font-semibold text-fg">{value}</p>
      </CardContent>
    </Card>
  );
}
