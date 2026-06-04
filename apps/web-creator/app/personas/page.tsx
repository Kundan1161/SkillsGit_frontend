"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Brain, PlusCircle } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  personasCreatorApi,
  type PersonaRead,
} from "@/lib/api/personas";

const STATUS_VARIANT: Record<
  string,
  "default" | "secondary" | "outline" | "destructive"
> = {
  draft: "outline",
  pending_review: "secondary",
  published: "default",
  unlisted: "destructive",
};

export default function PersonasListPage() {
  const [personas, setPersonas] = useState<PersonaRead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    personasCreatorApi.list().then((res) => {
      setPersonas(res.items);
      setLoading(false);
    });
  }, []);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">
              My personas
            </h1>
            <p className="mt-1 text-sm text-fg-muted">
              Each persona is an AI assistant built on your lived experience.
              Add neurons via Capture to grow the vault.
            </p>
          </div>
          <Button asChild>
            <Link href="/personas/new">
              <PlusCircle className="h-4 w-4" />
              New persona
            </Link>
          </Button>
        </div>

        <section className="mt-10">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24 w-full rounded-xl" />
              ))}
            </div>
          ) : personas.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20 text-center">
              <Brain className="mb-3 h-8 w-8 text-fg-subtle" />
              <p className="text-sm font-medium text-fg-muted">
                No personas yet
              </p>
              <p className="mt-1 text-xs text-fg-subtle">
                Create your first persona to start packaging your expertise.
              </p>
              <Button asChild className="mt-4" size="sm">
                <Link href="/personas/new">Create persona</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {personas.map((p) => (
                <Link
                  key={p.id}
                  href={`/personas/${p.id}`}
                  className="flex items-center gap-4 rounded-xl border border-border bg-bg-raised px-5 py-4 transition-colors hover:border-brand-500"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-500/10 text-brand-500">
                    <Brain className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-fg">{p.name}</p>
                    <p className="text-xs text-fg-subtle">
                      {p.parent_occupation_name} ·{" "}
                      {p.neuron_count}{" "}
                      {p.neuron_count === 1 ? "neuron" : "neurons"}
                    </p>
                  </div>
                  <Badge variant={STATUS_VARIANT[p.status] ?? "outline"}>
                    {p.status.replace("_", " ")}
                  </Badge>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
