"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  occupationsCreatorApi,
  personasCreatorApi,
  type OccupationOption,
} from "@/lib/api/personas";

export default function NewPersonaPage() {
  const router = useRouter();
  const [occupations, setOccupations] = useState<OccupationOption[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [intro, setIntro] = useState("");
  const [occupationId, setOccupationId] = useState("");
  const [yearsExp, setYearsExp] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [pricingModel, setPricingModel] = useState<"one_time" | "subscription" | "free">("subscription");
  const [priceCents, setPriceCents] = useState("");

  useEffect(() => {
    occupationsCreatorApi.listPublished().then((res) =>
      setOccupations(res.items),
    );
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!occupationId || !name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const persona = await personasCreatorApi.create({
        parent_occupation_id: occupationId,
        name: name.trim(),
        tagline: tagline.trim() || undefined,
        creator_intro_md: intro.trim() || undefined,
        years_of_experience: yearsExp ? Number(yearsExp) : undefined,
        specialization: specialization.trim() || undefined,
        pricing_model: pricingModel,
        one_time_price_cents:
          pricingModel === "one_time" && priceCents
            ? Math.round(Number(priceCents) * 100)
            : undefined,
        subscription_price_cents:
          pricingModel === "subscription" && priceCents
            ? Math.round(Number(priceCents) * 100)
            : undefined,
      });
      router.push(`/personas/${persona.id}`);
    } catch (e) {
      setError((e as { message?: string }).message ?? "Failed to create persona.");
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 md:px-8">
        <a
          href="/personas"
          className="mb-6 flex items-center gap-1 text-sm text-fg-muted hover:text-fg"
        >
          <ChevronLeft className="h-4 w-4" />
          My personas
        </a>

        <h1 className="text-2xl font-semibold tracking-tight">
          Create a persona
        </h1>
        <p className="mt-1 text-sm text-fg-muted">
          A persona is an AI assistant built on your real experiences. You'll
          add memory neurons after creation via Capture.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {/* Occupation */}
          <div className="space-y-1.5">
            <Label htmlFor="occupation">Parent occupation *</Label>
            <p className="text-xs text-fg-subtle">
              Buyers must hold an active occupation license to purchase this
              persona.
            </p>
            <Select value={occupationId} onValueChange={setOccupationId} required>
              <SelectTrigger id="occupation">
                <SelectValue placeholder="Select an occupation…" />
              </SelectTrigger>
              <SelectContent>
                {occupations.map((o) => (
                  <SelectItem key={o.id} value={o.id}>
                    {o.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {occupations.length === 0 && (
              <p className="text-xs text-warning">
                No published occupations found. A published occupation must exist
                before you can create a persona.
              </p>
            )}
          </div>

          <Separator />

          {/* Identity */}
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="name">Persona name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Jane — Senior DevOps Engineer"
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tagline">Tagline</Label>
              <Input
                id="tagline"
                value={tagline}
                onChange={(e) => setTagline(e.target.value)}
                placeholder="8 years of on-call war stories from production Kubernetes"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="intro">Creator introduction</Label>
              <Textarea
                id="intro"
                value={intro}
                onChange={(e) => setIntro(e.target.value)}
                rows={4}
                placeholder="Tell buyers about your background, what you specialise in, and what kinds of experiences you've captured…"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="yearsExp">Years of experience</Label>
                <Input
                  id="yearsExp"
                  type="number"
                  min={0}
                  max={50}
                  value={yearsExp}
                  onChange={(e) => setYearsExp(e.target.value)}
                  placeholder="8"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="specialization">Specialization</Label>
                <Input
                  id="specialization"
                  value={specialization}
                  onChange={(e) => setSpecialization(e.target.value)}
                  placeholder="Kubernetes, incident management"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Pricing */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold">Pricing</h2>
            <div className="space-y-1.5">
              <Label htmlFor="pricingModel">Model</Label>
              <Select
                value={pricingModel}
                onValueChange={(v) =>
                  setPricingModel(v as "one_time" | "subscription" | "free")
                }
              >
                <SelectTrigger id="pricingModel">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="subscription">Monthly subscription</SelectItem>
                  <SelectItem value="one_time">One-time purchase</SelectItem>
                  <SelectItem value="free">Free</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {pricingModel !== "free" && (
              <div className="space-y-1.5">
                <Label htmlFor="price">
                  Price (USD){" "}
                  <span className="text-fg-subtle">
                    {pricingModel === "subscription" ? "/ month" : "one-time"}
                  </span>
                </Label>
                <Input
                  id="price"
                  type="number"
                  min={0}
                  step={0.01}
                  value={priceCents}
                  onChange={(e) => setPriceCents(e.target.value)}
                  placeholder="15.00"
                />
              </div>
            )}
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}

          <div className="flex gap-3">
            <Button
              type="submit"
              disabled={submitting || !occupationId || !name.trim()}
            >
              {submitting ? "Creating…" : "Create persona"}
            </Button>
            <Button type="button" variant="outline" asChild>
              <a href="/personas">Cancel</a>
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
