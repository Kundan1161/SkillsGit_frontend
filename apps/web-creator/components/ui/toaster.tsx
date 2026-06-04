"use client";

import { Toaster as SonnerToaster } from "sonner";
import { useTheme } from "next-themes";

export function Toaster() {
  const { theme } = useTheme();
  return (
    <SonnerToaster
      theme={(theme ?? "dark") as "light" | "dark" | "system"}
      position="bottom-right"
      richColors
      closeButton
    />
  );
}
