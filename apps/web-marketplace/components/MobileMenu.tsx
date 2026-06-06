"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, ArrowRight } from "lucide-react";

const NAV_LINKS = [
  { href: "/explore", label: "Explore Experts" },
  { href: "/c/all", label: "Categories" },
  { href: "/creator/dashboard", label: "Creator Hub" },
  { href: "/#pricing", label: "Pricing" },
  { href: "/#how-it-works", label: "How It Works" },
] as const;

export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <div className="lg:hidden">
      <button
        type="button"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="flex h-10 w-10 items-center justify-center"
        style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "0.75rem", color: "var(--color-fg)" }}
      >
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {open && (
        <>
          {/* backdrop */}
          <button
            type="button"
            aria-hidden
            tabIndex={-1}
            onClick={close}
            className="fixed inset-0 z-40"
            style={{ background: "rgba(0,0,0,0.25)" }}
          />
          {/* panel */}
          <div
            className="fixed inset-x-3 top-[4.75rem] z-50 flex flex-col gap-1 p-3"
            style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-lg)", borderRadius: "1.25rem" }}
          >
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={close}
                className="rounded-xl px-4 py-3 text-sm font-semibold"
                style={{ color: "var(--color-fg-muted)" }}
              >
                {link.label}
              </Link>
            ))}
            <div className="my-1 h-px" style={{ background: "var(--color-border)" }} />
            <Link
              href="/sign-in"
              onClick={close}
              className="rounded-xl px-4 py-3 text-sm font-semibold"
              style={{ color: "var(--color-fg)" }}
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              onClick={close}
              className="neu-btn-brand mt-1 inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-bold text-white"
              style={{ borderRadius: "0.85rem" }}
            >
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
