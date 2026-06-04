import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import type { ReactNode } from "react";

import { ThemeProvider } from "@/lib/theme";
import { QueryProvider } from "@/lib/query-client";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "skillsgit Studio",
    template: "%s · skillsgit Studio",
  },
  description:
    "The authoring studio for AI skills. Build, preview, and publish skills.md files.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      // suppressHydrationWarning: next-themes toggles `class="dark"` on <html>
      // before React hydration. Without this, dev mode would spam warnings.
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen bg-bg text-fg antialiased">
        <ThemeProvider>
          <QueryProvider>
            <TooltipProvider delayDuration={150}>
              <a
                href="#main"
                className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-brand-500 focus:px-3 focus:py-1.5 focus:text-sm focus:text-white"
              >
                Skip to content
              </a>
              {children}
              <Toaster />
            </TooltipProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
