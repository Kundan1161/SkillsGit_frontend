import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

// Token CSS owned by Agent 1 in `packages/ui`. Imported here so the
// CSS variables defined under `:root` / `.dark` are available globally.
import "@skillsgit/ui/styles/tokens.css";
import "./globals.css";

import { ThemeProvider } from "@/lib/theme";
import { QueryProvider } from "@/lib/query-client";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { HeroPointerAurora } from "@/components/hero-pointer-aurora";
import { CustomCursor } from "@/components/CustomCursor";

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
    default: "Skills Marketplace",
    template: "%s · Skills Marketplace",
  },
  description: "AI-powered expertise, modular and reusable.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen overflow-x-hidden bg-bg text-fg antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded-md focus:bg-brand-500 focus:px-3 focus:py-1.5 focus:text-sm focus:text-white"
        >
          Skip to content
        </a>
        <ThemeProvider>
          <QueryProvider>
            <TooltipProvider>
              <HeroPointerAurora />
              <CustomCursor />
              <div className="relative z-10 flex min-h-screen flex-col">
                <SiteHeader />
                <main id="main" className="flex-1">
                  {children}
                </main>
                <SiteFooter />
              </div>
              <Toaster />
            </TooltipProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
