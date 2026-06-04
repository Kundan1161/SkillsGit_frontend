"use client";

import { useState } from "react";

import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { deliveryApi } from "@/lib/api/delivery";

interface Props {
  licenseId: string;
  version: string;
  disabled?: boolean;
}

export function DownloadButton({ licenseId, version, disabled }: Props) {
  const [busy, setBusy] = useState(false);

  async function onClick() {
    setBusy(true);
    try {
      const res = await deliveryApi.prepareDownload(licenseId);
      // Trigger download by navigating to the presigned URL.
      window.location.href = res.download_url;
    } catch (err) {
      const e = err as { message?: string; code?: string };
      toast.error(e.message ?? "Download failed", {
        description: e.code,
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <Button
      size="lg"
      variant="primary"
      onClick={onClick}
      disabled={disabled || busy}
    >
      {busy ? "Preparing…" : `Download skills.md (v${version})`}
    </Button>
  );
}
