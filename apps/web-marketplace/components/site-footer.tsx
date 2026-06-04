import Link from "next/link";

const FOOTER_LINKS = [
  {
    heading: "Marketplace",
    links: [
      { href: "/browse", label: "Browse skills" },
      { href: "/c/all", label: "Categories" },
      { href: "/search", label: "Search" },
    ],
  },
  {
    heading: "Creators",
    links: [
      { href: "/become-a-creator", label: "Become a creator" },
      { href: "/dashboard", label: "Creator dashboard" },
    ],
  },
  {
    heading: "Account",
    links: [
      { href: "/library", label: "My library" },
      { href: "/settings/account", label: "Settings" },
      { href: "/sign-in", label: "Sign in" },
    ],
  },
] as const;

export function SiteFooter() {
  return (
    <footer style={{ background: "var(--color-bg)", boxShadow: "0 -4px 20px rgba(166,162,153,0.2), 0 -2px 8px rgba(255,255,255,0.5)" }}>
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 md:grid-cols-4 md:px-8">
        {/* Brand column */}
        <div className="space-y-3">
          <Link href="/" className="group flex items-center gap-2">
            <span
              className="inline-flex h-8 w-8 items-center justify-center text-white text-xs font-black"
              style={{
                background: "linear-gradient(135deg, #7c3aed, #6366f1)",
                boxShadow: "4px 4px 10px rgba(124,58,237,0.35), -2px -2px 6px rgba(255,255,255,0.5)",
                borderRadius: "0.75rem",
              }}
            >
              SG
            </span>
            <span className="text-sm font-black" style={{ letterSpacing: "-0.02em" }}>
              SKILLS<span style={{ color: "#7c3aed" }}>GIT</span>
            </span>
          </Link>
          <p className="text-sm leading-relaxed text-fg-muted">
            AI-powered expertise, modular and reusable. Real knowledge. Real attribution.
          </p>
          <p className="text-xs text-fg-subtle">© {new Date().getFullYear()} SkillsGit</p>
        </div>

        {/* Link columns */}
        {FOOTER_LINKS.map((col) => (
          <div key={col.heading}>
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-fg-subtle">
              {col.heading}
            </p>
            <ul className="space-y-2.5">
              {col.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="hover-underline text-sm text-fg-muted"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </footer>
  );
}
