"use client";

import { use, useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { skillsApi, type SkillRead } from "@/lib/api/skills";

export default function EditSkillPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [skill, setSkill] = useState<SkillRead | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // listing form fields
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [supportUrl, setSupportUrl] = useState("");
  const [faqMd, setFaqMd] = useState("");

  // new-version sheet state
  const [newVersionFile, setNewVersionFile] = useState<File | null>(null);
  const [targetVersion, setTargetVersion] = useState("");
  const [changelog, setChangelog] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await skillsApi.listMine();
        if (cancelled) return;
        const found = list.find((s) => s.id === id);
        if (!found) {
          setErr("Skill not found.");
          return;
        }
        setSkill(found);
        setName(found.name);
        setTagline(found.tagline ?? "");
        setSupportUrl((found as unknown as { support_url?: string }).support_url ?? "");
        setFaqMd((found as unknown as { faq_md?: string }).faq_md ?? "");
      } catch (e) {
        if (!cancelled)
          setErr((e as { message?: string }).message ?? "Load failed");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  async function saveListing() {
    if (!skill) return;
    setBusy(true);
    try {
      const updated = await skillsApi.patch(skill.id, {
        name,
        tagline: tagline || null,
        ...({
          support_url: supportUrl || null,
          faq_md: faqMd || null,
        } as Partial<SkillRead>),
      });
      setSkill(updated);
      toast.success("Listing saved");
    } catch (e) {
      toast.error((e as { message?: string }).message ?? "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function publishNow() {
    if (!skill) return;
    setBusy(true);
    try {
      const updated = await skillsApi.publish(skill.id);
      setSkill(updated);
      toast.success(
        updated.status === "published"
          ? "Published"
          : "Submitted for review",
      );
    } catch (e) {
      toast.error((e as { message?: string }).message ?? "Publish failed");
    } finally {
      setBusy(false);
    }
  }

  async function uploadNewVersion() {
    if (!skill || !newVersionFile || !targetVersion) return;
    setBusy(true);
    try {
      await skillsApi.submitVersion(
        skill.id,
        newVersionFile,
        targetVersion,
        changelog || undefined,
      );
      toast.success(`Version ${targetVersion} uploaded`);
      setNewVersionFile(null);
      setTargetVersion("");
      setChangelog("");
    } catch (e) {
      toast.error((e as { message?: string }).message ?? "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  if (err) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <p className="text-danger">{err}</p>
      </section>
    );
  }
  if (!skill) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="mt-4 h-40 w-full" />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">
            {skill.name}
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            {skill.slug} · {skill.pricing_model}
            <Badge variant="secondary" className="ml-3">
              {skill.status}
            </Badge>
          </p>
        </div>
        {skill.status === "draft" ? (
          <Button variant="primary" disabled={busy} onClick={publishNow}>
            Submit for review
          </Button>
        ) : null}
      </header>

      <Tabs defaultValue="listing" className="mt-6">
        <TabsList>
          <TabsTrigger value="listing">Listing</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
        </TabsList>

        <TabsContent value="listing" className="mt-4 space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
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
          <div>
            <Label htmlFor="support">Support URL</Label>
            <Input
              id="support"
              type="url"
              value={supportUrl}
              onChange={(e) => setSupportUrl(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="faq">FAQ (markdown)</Label>
            <Textarea
              id="faq"
              rows={6}
              value={faqMd}
              onChange={(e) => setFaqMd(e.target.value)}
            />
          </div>
          <Button onClick={saveListing} disabled={busy}>
            Save listing
          </Button>
        </TabsContent>

        <TabsContent value="versions" className="mt-4 space-y-4">
          <p className="text-sm text-fg-muted">
            The latest released version is shown on the public detail page.
            Submitting a new version puts the skill back into pending_review.
          </p>
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="primary">New version</Button>
            </SheetTrigger>
            <SheetContent side="right">
              <SheetHeader>
                <SheetTitle>New version</SheetTitle>
                <SheetDescription>
                  Upload an updated skills.md. The validator runs on submit.
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-4">
                <div>
                  <Label htmlFor="target">Target version (semver)</Label>
                  <Input
                    id="target"
                    placeholder="1.1.0"
                    value={targetVersion}
                    onChange={(e) => setTargetVersion(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="md">skills.md</Label>
                  <Input
                    id="md"
                    type="file"
                    accept=".md,text/markdown"
                    onChange={(e) =>
                      setNewVersionFile(e.target.files?.[0] ?? null)
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="cl">Changelog</Label>
                  <Textarea
                    id="cl"
                    rows={4}
                    value={changelog}
                    onChange={(e) => setChangelog(e.target.value)}
                  />
                </div>
              </div>
              <SheetFooter className="mt-6">
                <Button
                  onClick={uploadNewVersion}
                  disabled={busy || !newVersionFile || !targetVersion}
                >
                  Upload
                </Button>
              </SheetFooter>
            </SheetContent>
          </Sheet>
        </TabsContent>
      </Tabs>
    </section>
  );
}
