"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { CheckSquare, Download, Loader2, Square } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { deliveryApi, type LicenseRead } from "@/lib/api/delivery";

interface PersonaLicense {
  license_id: string;
  persona_id: string;
  persona_name: string;
  persona_slug: string;
  persona_handle: string;
  neuron_count: number;
}

interface VaultCompositionResponse {
  occupation_license_id: string;
  available_persona_licenses: PersonaLicense[];
}

interface DownloadResult {
  download_url: string;
  expires_at: string;
  composed_hash: string;
}

export default function VaultDownloadPage({
  params,
}: {
  params: Promise<{ "license-id": string }>;
}) {
  const resolved = use(params);
  const licenseId = resolved["license-id"];

  const [license, setLicense] = useState<LicenseRead | null>(null);
  const [composition, setComposition] = useState<VaultCompositionResponse | null>(null);
  const [selectedPersonas, setSelectedPersonas] = useState<Set<string>>(new Set());
  const [downloading, setDownloading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [lic, comp] = await Promise.all([
          deliveryApi.getLicense(licenseId),
          api.get<VaultCompositionResponse>(
            `/v1/licenses/${licenseId}/vault/composition`,
          ),
        ]);
        if (cancelled) return;
        setLicense(lic);
        setComposition(comp);
        // Pre-select all available persona licenses
        setSelectedPersonas(
          new Set(comp.available_persona_licenses.map((p) => p.license_id)),
        );
      } catch (e) {
        if (!cancelled)
          setError((e as { message?: string }).message ?? "Failed to load.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [licenseId]);

  const togglePersona = (licId: string) => {
    setSelectedPersonas((prev) => {
      const next = new Set(prev);
      if (next.has(licId)) next.delete(licId);
      else next.add(licId);
      return next;
    });
  };

  const handleDownload = async () => {
    setDownloading(true);
    setError(null);
    try {
      const result = await api.post<DownloadResult>(
        `/v1/licenses/${licenseId}/vault`,
        {
          persona_license_ids: Array.from(selectedPersonas),
        },
      );
      setDownloadUrl(result.download_url);
      // Trigger browser download
      const a = document.createElement("a");
      a.href = result.download_url;
      a.download = `vault-${licenseId}.zip`;
      a.click();
    } catch (e) {
      setError((e as { message?: string }).message ?? "Download failed.");
    } finally {
      setDownloading(false);
    }
  };

  if (error && !license) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-10 md:px-8">
        <p className="text-danger">{error}</p>
      </section>
    );
  }

  if (!license || !composition) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-10 md:px-8 space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="mt-6 h-48 w-full" />
      </section>
    );
  }

  const personas = composition.available_persona_licenses;
  const selectedCount = selectedPersonas.size;

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 md:px-8">
      <nav className="mb-6 flex items-center gap-2 text-xs text-fg-subtle">
        <Link href="/library" className="hover:text-fg hover:underline">
          Library
        </Link>
        <span>/</span>
        <Link
          href={`/library/${licenseId}`}
          className="hover:text-fg hover:underline"
        >
          {license.skill.name}
        </Link>
        <span>/</span>
        <span className="text-fg">Download vault</span>
      </nav>

      <h1 className="text-2xl font-semibold tracking-tight">
        Download knowledge vault
      </h1>
      <p className="mt-1 text-sm text-fg-muted">
        Your composed vault zip includes the full occupation plus any persona
        overlays you select. Each answer from an AI agent using this vault
        will cite the exact neuron it consulted.
      </p>

      <Separator className="my-6" />

      {/* Occupation (always included) */}
      <div className="mb-4">
        <h2 className="mb-3 text-sm font-semibold text-fg-muted uppercase tracking-widest">
          Occupation (always included)
        </h2>
        <div className="flex items-center gap-3 rounded-lg border border-border bg-bg-raised px-4 py-3">
          <CheckSquare className="h-4 w-4 text-brand-500" />
          <div>
            <p className="text-sm font-medium text-fg">{license.skill.name}</p>
            <p className="text-xs text-fg-subtle">
              License #{licenseId.slice(0, 8)}
            </p>
          </div>
          <Badge className="ml-auto" variant="secondary">
            Occupation
          </Badge>
        </div>
      </div>

      {/* Persona overlays */}
      {personas.length > 0 && (
        <div className="mb-6">
          <h2 className="mb-3 text-sm font-semibold text-fg-muted uppercase tracking-widest">
            Persona overlays ({personas.length} available)
          </h2>
          <div className="space-y-2">
            {personas.map((p) => {
              const selected = selectedPersonas.has(p.license_id);
              return (
                <button
                  key={p.license_id}
                  onClick={() => togglePersona(p.license_id)}
                  className="flex w-full items-center gap-3 rounded-lg border border-border bg-bg-raised px-4 py-3 text-left transition-colors hover:border-brand-500"
                >
                  {selected ? (
                    <CheckSquare className="h-4 w-4 shrink-0 text-brand-500" />
                  ) : (
                    <Square className="h-4 w-4 shrink-0 text-fg-subtle" />
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-fg">
                      {p.persona_name}
                    </p>
                    <p className="text-xs text-fg-subtle">
                      {p.neuron_count} neurons
                    </p>
                  </div>
                  <Badge className="ml-auto shrink-0" variant="outline">
                    Persona
                  </Badge>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {personas.length === 0 && (
        <Card className="mb-6">
          <CardContent className="py-4">
            <p className="text-sm text-fg-muted">
              You don&apos;t have any persona overlay licenses for this
              occupation.{" "}
              <Link
                href={`/occupations/${license.skill.creator_handle ?? ""}/${license.skill.slug}`}
                className="text-brand-500 hover:underline"
              >
                Browse persona overlays
              </Link>
            </p>
          </CardContent>
        </Card>
      )}

      {error && (
        <p className="mb-4 text-sm text-danger">{error}</p>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Button
          size="lg"
          onClick={handleDownload}
          disabled={downloading}
          className="sm:w-auto w-full"
        >
          {downloading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Download className="mr-2 h-4 w-4" />
          )}
          {downloading
            ? "Composing vault…"
            : `Download vault${selectedCount > 0 ? ` (${selectedCount + 1} components)` : ""}`}
        </Button>
        {downloadUrl && (
          <a
            href={downloadUrl}
            download
            className="text-sm text-brand-500 hover:underline"
          >
            Re-download last build
          </a>
        )}
      </div>

      <p className="mt-4 text-xs text-fg-subtle">
        The download link expires in 60 minutes. Each download is
        watermarked with your license ID for audit purposes.
      </p>
    </section>
  );
}
