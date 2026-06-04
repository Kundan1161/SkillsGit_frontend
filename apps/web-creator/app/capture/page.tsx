"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Brain, PlusCircle } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { captureApi, type CaptureSessionRead } from "@/lib/api/capture";
import { occupationsCreatorApi, personasCreatorApi, type PersonaRead } from "@/lib/api/personas";

const STATUS_LABELS: Record<string, { label: string; variant: "default" | "secondary" | "outline" | "destructive" }> = {
  draft: { label: "Draft", variant: "outline" },
  extracting: { label: "Extracting…", variant: "secondary" },
  draft_ready: { label: "Review needed", variant: "default" },
  finalizing: { label: "Finalizing…", variant: "secondary" },
  finalized: { label: "Published", variant: "default" },
  abandoned: { label: "Abandoned", variant: "destructive" },
};

export default function CaptureLandingPage() {
  const router = useRouter();

  const [sessions, setSessions] = useState<CaptureSessionRead[]>([]);
  const [personas, setPersonas] = useState<PersonaRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  // New session dialog state
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [personaId, setPersonaId] = useState("");

  useEffect(() => {
    Promise.all([
      captureApi.listSessions({ status: "draft,extracting,draft_ready" }),
      personasCreatorApi.list(),
    ]).then(([sessRes, persRes]) => {
      setSessions(sessRes.items);
      setPersonas(persRes.items);
      setLoading(false);
    });
  }, []);

  const handleCreate = async () => {
    if (!title.trim() || !personaId) return;
    setCreating(true);
    try {
      const session = await captureApi.createSession({
        persona_id: personaId,
        title: title.trim(),
      });
      router.push(`/capture/${session.id}`);
    } catch {
      setCreating(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">
              Capture
            </h1>
            <p className="mt-1 text-sm text-fg-muted">
              Describe a real experience. AI will structure it into a memory
              neuron and add it to your persona vault.
            </p>
          </div>

          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <PlusCircle className="h-4 w-4" />
                New capture
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Start a new capture session</DialogTitle>
                <DialogDescription>
                  Pick the persona this neuron belongs to and give the
                  experience a working title.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-2">
                <div className="space-y-1.5">
                  <Label htmlFor="capture-title">Title</Label>
                  <Input
                    id="capture-title"
                    placeholder="e.g. Flaky CI after Redis upgrade"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="capture-persona">Persona</Label>
                  <Select value={personaId} onValueChange={setPersonaId}>
                    <SelectTrigger id="capture-persona">
                      <SelectValue placeholder="Select a persona…" />
                    </SelectTrigger>
                    <SelectContent>
                      {personas.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {personas.length === 0 && (
                    <p className="text-xs text-fg-subtle">
                      You need a persona first.{" "}
                      <a href="/personas/new" className="text-brand-500 hover:underline">
                        Create one
                      </a>
                    </p>
                  )}
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={creating || !title.trim() || !personaId}
                >
                  {creating ? "Creating…" : "Start capturing"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <section className="mt-10">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-widest text-fg-subtle">
            In progress
          </h2>

          {loading ? (
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <Skeleton key={i} className="h-20 w-full rounded-xl" />
              ))}
            </div>
          ) : sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
              <Brain className="mb-3 h-8 w-8 text-fg-subtle" />
              <p className="text-sm font-medium text-fg-muted">
                No captures in progress
              </p>
              <p className="mt-1 text-xs text-fg-subtle">
                Start a new capture to turn a recent experience into a memory
                neuron.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((s) => {
                const st = STATUS_LABELS[s.status] ?? STATUS_LABELS.draft;
                return (
                  <a
                    key={s.id}
                    href={`/capture/${s.id}`}
                    className="flex items-center justify-between gap-4 rounded-xl border border-border bg-bg-raised px-5 py-4 transition-colors hover:border-brand-500"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium text-fg">{s.title}</p>
                      <p className="mt-0.5 text-xs text-fg-subtle">
                        {new Date(s.created_at).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </p>
                    </div>
                    <Badge variant={st.variant}>{st.label}</Badge>
                  </a>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
