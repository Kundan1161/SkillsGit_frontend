"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { skillsApi, type PricingModel } from "@/lib/api/skills";

const FALLBACK_CATEGORIES = [
  { slug: "finance", name: "Finance" },
  { slug: "design", name: "Design" },
  { slug: "data", name: "Data" },
  { slug: "marketing", name: "Marketing" },
  { slug: "sales", name: "Sales" },
  { slug: "engineering", name: "Engineering" },
  { slug: "operations", name: "Operations" },
  { slug: "productivity", name: "Productivity" },
  { slug: "other", name: "Other" },
];

interface FieldError {
  field: string;
  code: string;
  message: string;
}

export default function NewSkillPage() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FieldError[]>([]);

  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [category, setCategory] = useState("other");
  const [tags, setTags] = useState("");
  const [pricingModel, setPricingModel] = useState<PricingModel>("free");
  const [priceCents, setPriceCents] = useState<number | "">("");
  const [supportUrl, setSupportUrl] = useState("");
  const [skillsMd, setSkillsMd] = useState<File | null>(null);
  const [coverImage, setCoverImage] = useState<File | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!skillsMd) {
      toast.error("Upload a skills.md file");
      return;
    }
    setBusy(true);
    setErrors([]);
    try {
      const result = await skillsApi.create({
        name,
        tagline: tagline || undefined,
        category,
        tags,
        pricing_model: pricingModel,
        one_time_price_cents:
          pricingModel === "one_time" && priceCents !== ""
            ? Number(priceCents)
            : undefined,
        support_url: supportUrl || undefined,
        skills_md: skillsMd,
        cover_image: coverImage,
      });
      toast.success("Draft created");
      router.push(`/dashboard/skills/${result.id}`);
    } catch (e) {
      const err = e as {
        message?: string;
        code?: string;
        details?: { error?: { details?: FieldError[] } };
      };
      const detailList = err.details?.error?.details;
      if (Array.isArray(detailList)) {
        setErrors(detailList);
      }
      toast.error(err.message ?? "Failed to create skill", {
        description: err.code,
      });
    } finally {
      setBusy(false);
    }
  }

  function errorFor(field: string) {
    return errors.find((e) => e.field.endsWith(field))?.message;
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight">New skill</h1>
      <p className="mt-2 text-fg-muted">
        Upload a <code>skills.md</code> file. Validation runs on submit.
      </p>

      <form className="mt-8 space-y-5" onSubmit={onSubmit}>
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div>
          <Label htmlFor="tagline">Tagline</Label>
          <Input
            id="tagline"
            value={tagline}
            onChange={(e) => setTagline(e.target.value)}
            maxLength={140}
          />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="category">Category</Label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger id="category">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FALLBACK_CATEGORIES.map((c) => (
                  <SelectItem key={c.slug} value={c.slug}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="tags">Tags (comma-separated)</Label>
            <Input
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="dcf, valuation"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="pm">Pricing model</Label>
            <Select
              value={pricingModel}
              onValueChange={(v) => setPricingModel(v as PricingModel)}
            >
              <SelectTrigger id="pm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="one_time">One-time</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {pricingModel === "one_time" ? (
            <div>
              <Label htmlFor="price">Price (cents)</Label>
              <Input
                id="price"
                type="number"
                min={1}
                value={priceCents}
                onChange={(e) =>
                  setPriceCents(e.target.value === "" ? "" : Number(e.target.value))
                }
              />
            </div>
          ) : null}
        </div>

        <div>
          <Label htmlFor="support">Support URL (optional)</Label>
          <Input
            id="support"
            type="url"
            value={supportUrl}
            onChange={(e) => setSupportUrl(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="cover">Cover image (optional)</Label>
          <Input
            id="cover"
            type="file"
            accept="image/*"
            onChange={(e) => setCoverImage(e.target.files?.[0] ?? null)}
          />
        </div>

        <div>
          <Label htmlFor="md">skills.md</Label>
          <Input
            id="md"
            type="file"
            accept=".md,text/markdown"
            onChange={(e) => setSkillsMd(e.target.files?.[0] ?? null)}
            required
          />
          {errorFor("body") || errorFor("frontmatter") ? (
            <p className="mt-1 text-sm text-danger">
              {errorFor("body") ?? errorFor("frontmatter")}
            </p>
          ) : null}
        </div>

        {errors.length > 0 ? (
          <div className="rounded-md border border-danger/40 bg-danger/10 p-3 text-sm">
            <strong>Validation errors:</strong>
            <ul className="mt-1 list-disc pl-5">
              {errors.map((e, i) => (
                <li key={i}>
                  <code>{e.field}</code>: {e.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div>
          <Button type="submit" variant="primary" disabled={busy}>
            {busy ? "Uploading…" : "Create draft"}
          </Button>
        </div>
      </form>
    </section>
  );
}
