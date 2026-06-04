"use client";

import { use, useEffect, useState } from "react";

import { DownloadButton } from "@/components/library/DownloadButton";
import { VersionPicker } from "@/components/library/VersionPicker";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { deliveryApi, type LicenseRead } from "@/lib/api/delivery";

export default function LicensePage({
  params,
}: {
  params: Promise<{ "license-id": string }>;
}) {
  const resolved = use(params);
  const licenseId = resolved["license-id"];
  const [license, setLicense] = useState<LicenseRead | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await deliveryApi.getLicense(licenseId);
        if (!cancelled) setLicense(data);
      } catch (e) {
        const msg = (e as { message?: string }).message ?? "Not found.";
        if (!cancelled) setErr(msg);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [licenseId]);

  if (err) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <p className="text-danger">{err}</p>
      </section>
    );
  }
  if (license === null) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="mt-4 h-32 w-full" />
      </section>
    );
  }

  const cv = license.current_version;
  return (
    <section className="mx-auto max-w-3xl px-4 py-10 md:px-8">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">
            {license.skill.name}
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            by{" "}
            {license.skill.creator_handle
              ? `@${license.skill.creator_handle}`
              : "unknown"}{" "}
            · License type: {license.source} · Status: {license.status}
          </p>
        </div>
        <Badge variant="secondary">{license.source}</Badge>
      </header>

      <div className="mt-8 rounded-lg border border-border p-6">
        <h2 className="text-lg font-semibold">Download</h2>
        {cv ? (
          <>
            <p className="mt-1 text-sm text-fg-muted">
              Entitled to version {cv.version}. A fresh watermarked copy is
              generated each time you click — keep one per machine.
            </p>
            <div className="mt-4">
              <DownloadButton licenseId={license.id} version={cv.version} />
            </div>
            {license.last_downloaded_at ? (
              <p className="mt-3 text-xs text-fg-muted">
                Last downloaded{" "}
                {new Date(license.last_downloaded_at).toLocaleString()} ·{" "}
                {license.download_count} total
              </p>
            ) : null}
          </>
        ) : (
          <p className="mt-1 text-sm text-fg-muted">
            No version is currently available for this license.
          </p>
        )}
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">Version history</h2>
        <div className="mt-3">
          <VersionPicker
            versions={cv ? [{ ...cv }] : []}
            currentVersion={cv?.version ?? null}
          />
        </div>
      </div>

      {license.source === "one_time" &&
      !license.last_downloaded_at &&
      new Date().getTime() - new Date(license.granted_at).getTime() <
        14 * 24 * 60 * 60 * 1000 ? (
        <p className="mt-8 text-sm">
          Within refund window —{" "}
          <a
            href="/settings/billing"
            className="text-brand-500 underline-offset-4 hover:underline"
          >
            Request refund
          </a>
          .
        </p>
      ) : null}
    </section>
  );
}
