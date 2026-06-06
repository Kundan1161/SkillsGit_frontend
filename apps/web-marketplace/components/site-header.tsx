import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { MobileMenu } from "@/components/MobileMenu";

const NAV_LINKS = [
  { href: "/explore",            label: "Explore Experts" },
  { href: "/c/all",              label: "Categories" },
  { href: "/creator/dashboard",  label: "Creator Hub" },
  { href: "/#pricing",           label: "Pricing" },
  { href: "/#how-it-works",      label: "How It Works" },
] as const;

export function SiteHeader() {
  return (
    <header
      className="sticky top-0 z-40 w-full"
      style={{
        background: "var(--color-bg)",
        boxShadow: "0 4px 20px rgba(166,162,153,0.35), 0 -2px 8px rgba(255,255,255,0.6)",
      }}
    >
      <div className="mx-auto flex h-18 max-w-7xl items-center justify-between gap-4 px-6 py-4 md:px-10 lg:px-16">
        {/* Logo — neumorphic pill */}
        <Link href="/" className="group flex items-center gap-3">
          <div
            className="flex h-10 w-10 items-center justify-center text-white text-xs font-black transition-all duration-200"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #6366f1)",
              boxShadow: "4px 4px 10px rgba(124,58,237,0.35), -2px -2px 6px rgba(255,255,255,0.5)",
              borderRadius: "0.875rem",
            }}
          >
            SG
          </div>
          <span className="text-sm font-black tracking-tight" style={{ letterSpacing: "-0.02em" }}>
            SKILLS<span style={{ color: "#7c3aed" }}>GIT</span>
          </span>
        </Link>

        {/* Nav — neumorphic pill container */}
        <nav
          className="hidden items-center gap-1 px-2 py-2 lg:flex"
          style={{
            background: "var(--color-bg)",
            boxShadow: "var(--shadow-neu-inset-sm)",
            borderRadius: "9999px",
          }}
        >
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="neu-nav-link hover-shimmer whitespace-nowrap rounded-full px-3 py-1.5 text-sm font-semibold xl:px-4"
              style={{ color: "var(--color-fg-muted)" }}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link
            href="/sign-in"
            className="chip-hover hidden rounded-full px-4 py-2 text-sm font-medium sm:block"
            style={{ color: "var(--color-fg-muted)", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)" }}
          >
            Sign in
          </Link>
          <Link
            href="/sign-up"
            className="neu-btn-brand ripple hidden items-center gap-1.5 rounded-full px-5 py-2 text-sm font-bold text-white sm:inline-flex"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #6366f1)",
              boxShadow: "4px 4px 12px rgba(124,58,237,0.4), -2px -2px 8px rgba(255,255,255,0.4)",
            }}
          >
            Get started <ArrowRight className="h-3.5 w-3.5" />
          </Link>

          <MobileMenu />
        </div>
      </div>
    </header>
  );
}
