"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronLeft, GripVertical, Loader2, Trash2 } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  personasCreatorApi,
  type NeuronRead,
} from "@/lib/api/personas";

export default function NeuronsOrderPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [neurons, setNeurons] = useState<NeuronRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dragIdx = useRef<number | null>(null);

  useEffect(() => {
    personasCreatorApi.listNeurons(id).then((res) => {
      setNeurons(res.items);
      setLoading(false);
    });
  }, [id]);

  const handleDragStart = (idx: number) => {
    dragIdx.current = idx;
  };

  const handleDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault();
    const from = dragIdx.current;
    if (from === null || from === idx) return;
    setNeurons((prev) => {
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(idx, 0, moved);
      dragIdx.current = idx;
      return next;
    });
    setDirty(true);
  };

  const handleRemove = async (neuronId: string) => {
    try {
      await personasCreatorApi.removeNeuron(id, neuronId);
      setNeurons((prev) => prev.filter((n) => n.id !== neuronId));
    } catch (e) {
      setError((e as { message?: string }).message ?? "Remove failed.");
    }
  };

  const handleSaveOrder = async () => {
    setSaving(true);
    setError(null);
    try {
      await personasCreatorApi.reorderNeurons(
        id,
        neurons.map((n, i) => ({
          neuron_skill_id: n.id,
          sort_order: i,
        })),
      );
      setDirty(false);
    } catch (e) {
      setError((e as { message?: string }).message ?? "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 md:px-8">
        <div className="mb-6 flex items-center gap-3">
          <Link
            href={`/personas/${id}`}
            className="flex items-center gap-1 text-sm text-fg-muted hover:text-fg"
          >
            <ChevronLeft className="h-4 w-4" />
            Persona
          </Link>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Manage neurons
            </h1>
            <p className="mt-1 text-sm text-fg-muted">
              Drag to reorder. Order affects how neurons appear in the vault.
            </p>
          </div>
          {dirty && (
            <Button onClick={handleSaveOrder} disabled={saving} size="sm">
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {saving ? "Saving…" : "Save order"}
            </Button>
          )}
        </div>

        {error && <p className="mt-3 text-sm text-danger">{error}</p>}

        <Separator className="my-6" />

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-16 w-full rounded-xl" />
            ))}
          </div>
        ) : neurons.length === 0 ? (
          <p className="text-sm text-fg-muted">No neurons yet.</p>
        ) : (
          <div className="space-y-2">
            {neurons.map((n, i) => (
              <div
                key={n.id}
                draggable
                onDragStart={() => handleDragStart(i)}
                onDragOver={(e) => handleDragOver(e, i)}
                onDragEnd={() => (dragIdx.current = null)}
                className="flex cursor-grab items-center gap-3 rounded-xl border border-border bg-bg-raised px-4 py-3 active:cursor-grabbing"
              >
                <GripVertical className="h-4 w-4 shrink-0 text-fg-subtle" />
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
                  <Badge variant="outline" className="shrink-0 text-[10px]">
                    {n.section}
                  </Badge>
                )}
                <button
                  onClick={() => handleRemove(n.id)}
                  className="ml-1 shrink-0 rounded p-1 text-fg-subtle hover:text-danger focus:outline-none"
                  title="Remove neuron from persona"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {dirty && (
          <div className="mt-6 flex gap-3">
            <Button onClick={handleSaveOrder} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {saving ? "Saving…" : "Save order"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                personasCreatorApi.listNeurons(id).then((res) => {
                  setNeurons(res.items);
                  setDirty(false);
                });
              }}
            >
              Discard changes
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}
