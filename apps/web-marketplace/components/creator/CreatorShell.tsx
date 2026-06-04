import Link from "next/link";
import { Upload, Database, User, Play, Store, Users, TrendingUp, Settings, Brain } from "lucide-react";

const NAV = [
  { icon: Upload,    label: "Upload Knowledge", href: "/creator/upload",      key: "upload" },
  { icon: Database,  label: "View Vault",        href: "/creator/vault",       key: "vault" },
  { icon: User,      label: "Edit Persona",      href: "/creator/persona",     key: "persona" },
  { icon: Play,      label: "Preview AI",        href: "/creator/preview",     key: "preview" },
  { icon: Store,     label: "Manage Listing",    href: "/creator/listing",     key: "listing" },
  { icon: Users,     label: "Subscribers",       href: "/creator/subscribers", key: "subscribers" },
  { icon: TrendingUp,label: "Earnings",          href: "/creator/earnings",    key: "earnings" },
  { icon: Settings,  label: "Settings",          href: "/creator/settings",    key: "settings" },
];

interface CreatorShellProps {
  children: React.ReactNode;
  /** Which nav item is currently active — matches the `key` field */
  active?: string;
}

export function CreatorShell({ children, active }: CreatorShellProps) {
  return (
    <div style={{ background: "var(--color-bg)", minHeight: "100vh" }}>
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-16">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[220px_1fr]">

          {/* ── Sidebar ── */}
          <aside>
            <div
              className="sticky top-24 flex flex-col gap-1"
              style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-lg)", borderRadius: "1.5rem", padding: "1rem" }}
            >
              {/* Creator identity */}
              <div className="px-4 py-3 mb-2">
                <div className="flex items-center gap-3">
                  <div
                    style={{
                      width: 40, height: 40, borderRadius: "50%",
                      background: "linear-gradient(135deg,#7c3aed,#6366f1)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      boxShadow: "4px 4px 10px rgba(124,58,237,0.3),-2px -2px 6px rgba(255,255,255,0.5)",
                    }}
                  >
                    <Brain className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-black" style={{ color: "var(--color-fg)", letterSpacing: "-0.02em" }}>Marcus Webb</p>
                    <p className="tag-label">DevOps Expert</p>
                  </div>
                </div>
              </div>

              {/* Nav items */}
              {NAV.map((item) => {
                const Icon = item.icon;
                const isActive = item.key === active;
                return (
                  <Link
                    key={item.key}
                    href={item.href}
                    className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150"
                    style={{
                      color: isActive ? "#7c3aed" : "var(--color-fg-muted)",
                      background: "var(--color-bg)",
                      boxShadow: isActive ? "var(--shadow-neu-inset-sm)" : "none",
                    }}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {item.label}
                  </Link>
                );
              })}

              {/* Back to marketplace */}
              <div className="mt-3 pt-3" style={{ borderTop: "1px solid rgba(166,162,153,0.15)" }}>
                <Link
                  href="/"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold"
                  style={{ color: "var(--color-fg-subtle)" }}
                >
                  ← Marketplace
                </Link>
              </div>
            </div>
          </aside>

          {/* ── Main content ── */}
          <main>{children}</main>
        </div>
      </div>
    </div>
  );
}
