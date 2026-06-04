"use client";

import { useTheme } from "next-themes";
import { Toaster as Sonner, type ToasterProps } from "sonner";

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "light" } = useTheme();
  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-bg-raised group-[.toaster]:text-fg group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-fg-muted",
          actionButton:
            "group-[.toast]:bg-brand-500 group-[.toast]:text-white",
          cancelButton:
            "group-[.toast]:bg-bg-muted group-[.toast]:text-fg-muted",
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
