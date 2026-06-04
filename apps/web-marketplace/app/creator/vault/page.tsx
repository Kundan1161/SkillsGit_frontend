import Link from "next/link";
import { Database, FileText, Video, Music, Image, Eye, Edit, RefreshCw, CheckCircle, ArrowRight } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const vaultFiles = [
  { name: "advanced-kubernetes-patterns.pdf", type: "PDF", icon: FileText, color: "#7c3aed", size: "2.4 MB", tokens: "18,420", status: "approved", date: "Jun 2, 2025" },
  { name: "devops-incident-response.mp4",     type: "Video", icon: Video,    color: "#3b82f6", size: "156 MB",  tokens: "42,100", status: "approved", date: "May 28, 2025" },
  { name: "architecture-decisions.md",         type: "Markdown", icon: FileText, color: "#10b981", size: "12 KB",   tokens: "3,200",  status: "approved", date: "May 20, 2025" },
  { name: "on-call-runbook.pdf",               type: "PDF", icon: FileText, color: "#f59e0b", size: "890 KB",  tokens: "9,800",  status: "review",   date: "Jun 3, 2025" },
  { name: "k8s-cost-optimization.mp3",         type: "Audio", icon: Music,   color: "#f43f5e", size: "48 MB",   tokens: "21,340", status: "approved", date: "Apr 15, 2025" },
  { name: "infra-diagrams.png",                type: "Image", icon: Image,   color: "#06b6d4", size: "3.1 MB",  tokens: "1,240",  status: "approved", date: "Mar 30, 2025" },
];

const totalTokens = "96,100";
const vaultScore  = 94;

export default function VaultPage() {
  return (
    <CreatorShell active="vault">
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
              Markdown <span className="gradient-text">Vault</span>
            </h1>
            <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>Inspect every piece of knowledge your AI learned from.</p>
          </div>
          <div className="flex gap-3">
            <div className="neu px-5 py-3 text-center">
              <p className="text-2xl font-black gradient-text">{vaultScore}%</p>
              <p className="tag-label">AI Readiness</p>
            </div>
            <div className="neu px-5 py-3 text-center">
              <p className="text-2xl font-black" style={{ color: "var(--color-fg)" }}>{totalTokens}</p>
              <p className="tag-label">Total Tokens</p>
            </div>
          </div>
        </div>

        {/* Vault completeness bar */}
        <div className="neu-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-bold" style={{ color: "var(--color-fg)" }}>Vault Completeness</span>
            <span className="tag-label gradient-text">{vaultScore}%</span>
          </div>
          <div style={{ height: 8, borderRadius: "9999px", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset-sm)" }}>
            <div style={{ height: "100%", width: `${vaultScore}%`, borderRadius: "9999px", background: "linear-gradient(90deg,#7c3aed,#6366f1)", boxShadow: "0 0 12px rgba(124,58,237,0.4)" }} />
          </div>
          <p className="mt-3 text-xs" style={{ color: "var(--color-fg-subtle)" }}>
            Add more files to reach 100% — focus on edge cases and FAQ content.
          </p>
        </div>

        {/* File list */}
        <div className="flex flex-col gap-3">
          {vaultFiles.map((f) => {
            const Icon = f.icon;
            return (
              <div key={f.name} className="neu p-5 flex items-center gap-4">
                {/* Type icon */}
                <div style={{ width: 44, height: 44, borderRadius: "0.875rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Icon className="h-5 w-5" style={{ color: f.color }} />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold truncate" style={{ color: "var(--color-fg)" }}>{f.name}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="tag-label" style={{ color: f.color }}>{f.type}</span>
                    <span style={{ fontSize: "0.65rem", color: "var(--color-fg-subtle)" }}>{f.size}</span>
                    <span style={{ fontSize: "0.65rem", color: "var(--color-fg-subtle)" }}>{f.tokens} tokens</span>
                    <span style={{ fontSize: "0.65rem", color: "var(--color-fg-subtle)" }}>{f.date}</span>
                  </div>
                </div>

                {/* Status */}
                <div
                  className="flex items-center gap-1.5 px-3 py-1.5"
                  style={{
                    background: "var(--color-bg)",
                    boxShadow: f.status === "approved" ? "var(--shadow-neu-inset-sm)" : "var(--shadow-neu-sm)",
                    borderRadius: "9999px",
                  }}
                >
                  <CheckCircle className="h-3 w-3" style={{ color: f.status === "approved" ? "#10b981" : "#f59e0b" }} />
                  <span style={{ fontSize: "0.65rem", fontWeight: 700, color: f.status === "approved" ? "#10b981" : "#f59e0b", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                    {f.status}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2 shrink-0">
                  {[
                    { Icon: Eye,       label: "Preview"    },
                    { Icon: Edit,      label: "Edit"       },
                    { Icon: RefreshCw, label: "Regenerate" },
                  ].map(({ Icon: A, label }) => (
                    <button
                      key={label}
                      title={label}
                      style={{ width: 32, height: 32, borderRadius: "0.5rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}
                    >
                      <A className="h-3.5 w-3.5" style={{ color: "var(--color-fg-subtle)" }} />
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <Link href="/creator/upload" className="neu-btn-brand inline-flex items-center gap-2 px-6 py-3 text-sm font-bold text-white w-fit" style={{ borderRadius: "1rem" }}>
          Add more knowledge <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </CreatorShell>
  );
}
