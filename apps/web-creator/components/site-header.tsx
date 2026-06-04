import Link from "next/link";
import { ExternalLink, Sparkles } from "lucide-react";
import { UserMenu } from "@/components/user-menu";

const MARKETPLACE_URL =
  process.env.NEXT_PUBLIC_MARKETPLACE_URL ?? "http://localhost:3000";

const NAV: Array<{ href: string; label: string }> = [
  { href: "/", label: "Drafts" },
  { href: "/personas", label: "Personas" },
  { href: "/capture", label: "Capture" },
  { href: "/templates", label: "Templates" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-bg/85 backdrop-blur-xl backdrop-saturate-150">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4 md:px-8">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-2 shrink-0">
          <span className="inline-flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-sm shadow-brand-500/25 transition-shadow group-hover:shadow-md group-hover:shadow-brand-500/35">
            <Sparkles className="h-3.5 w-3.5" aria-hidden />
          </span>
          <span className="text-sm font-semibold tracking-tight">
            Skills<span className="text-brand-500">Git</span>
          </span>
          <span className="rounded-full border border-brand-500/20 bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
            Studio
          </span>
        </Link>

        {/* Nav */}
        <nav className="hidden items-center gap-0.5 text-sm md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-3 py-1.5 font-medium text-fg-muted transition-colors hover:bg-bg-muted hover:text-fg"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <a
            href={MARKETPLACE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium text-fg-muted transition-colors hover:bg-bg-muted hover:text-fg md:flex"
          >
            <ExternalLink className="h-3 w-3" />
            Marketplace
          </a>
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
