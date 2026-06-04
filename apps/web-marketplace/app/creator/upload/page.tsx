"use client";
import { Upload, FileText, Video, Headphones, Image, File, CheckCircle } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const formats = [
  { icon: FileText, label: "PDF" },
  { icon: Video, label: "Video" },
  { icon: Headphones, label: "Audio" },
  { icon: FileText, label: "Notes" },
  { icon: Image, label: "Images" },
  { icon: FileText, label: "Markdown" },
];

const queue = [
  { name: "advanced-kubernetes-patterns.pdf", type: "PDF", size: "2.4 MB", status: "Complete", progress: 100 },
  { name: "devops-incident-response.mp4", type: "Video", size: "156 MB", status: "Processing", progress: 67 },
  { name: "architecture-decisions.md", type: "Markdown", size: "12 KB", status: "Complete", progress: 100 },
  { name: "on-call-runbook.pdf", type: "PDF", size: "890 KB", status: "Processing", progress: 34 },
];

const statusColor: Record<string, string> = {
  Complete: "#10b981",
  Processing: "#f59e0b",
  Failed: "#ef4444",
};

export default function UploadPage() {
  return (
    <CreatorShell active="upload">
      <div className="max-w-3xl">
        <div className="mb-10">
          <span className="tag-label block mb-2">Knowledge Vault</span>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            Upload <span className="gradient-text">Knowledge</span>
          </h1>
        </div>

        {/* Drop zone */}
        <div
          className="neu-inset mb-8 flex flex-col items-center justify-center gap-5 py-20 px-8 text-center"
          style={{
            borderRadius: "var(--radius-2xl)",
            border: "2px dashed rgba(124,58,237,0.25)",
            cursor: "pointer",
          }}
        >
          <div
            style={{
              width: 80, height: 80, borderRadius: "50%",
              background: "var(--color-bg)",
              boxShadow: "var(--shadow-neu-md)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >
            <Upload className="h-8 w-8" style={{ color: "#7c3aed" }} />
          </div>
          <div>
            <p className="text-lg font-bold" style={{ color: "var(--color-fg)" }}>Drag & drop your files here</p>
            <p className="text-sm mt-1" style={{ color: "var(--color-fg-muted)" }}>or click to browse your computer</p>
          </div>
          <button className="neu-btn-brand px-6 py-2.5 text-sm font-bold text-white">
            Choose Files
          </button>
        </div>

        {/* Accepted formats */}
        <div className="mb-8">
          <p className="tag-label mb-4">Accepted Formats</p>
          <div className="flex flex-wrap gap-3">
            {formats.map(({ icon: Icon, label }) => (
              <div key={label} className="neu-sm flex items-center gap-2 px-4 py-2">
                <Icon className="h-4 w-4" style={{ color: "#7c3aed" }} />
                <span className="text-sm font-semibold" style={{ color: "var(--color-fg-muted)" }}>{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Processing queue */}
        <div className="neu-lg p-6">
          <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-fg)" }}>Processing Queue</h2>
          <div className="flex flex-col gap-4">
            {queue.map((file, i) => (
              <div key={i} className="neu-inset p-4" style={{ borderRadius: "var(--radius-lg)" }}>
                <div className="flex items-center gap-4">
                  <div className="neu p-2.5 rounded-lg shrink-0">
                    <File className="h-4 w-4" style={{ color: "#7c3aed" }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-4 mb-2">
                      <p className="text-sm font-semibold truncate" style={{ color: "var(--color-fg)" }}>{file.name}</p>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className="tag-label">{file.type}</span>
                        <span className="text-xs" style={{ color: "var(--color-fg-subtle)" }}>{file.size}</span>
                        <span className="text-xs font-bold flex items-center gap-1" style={{ color: statusColor[file.status] }}>
                          {file.status === "Complete" && <CheckCircle className="h-3 w-3" />}
                          {file.status}
                        </span>
                      </div>
                    </div>
                    {/* Progress bar */}
                    <div className="neu-inset h-2" style={{ borderRadius: "9999px" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${file.progress}%`,
                          background: file.status === "Complete"
                            ? "linear-gradient(90deg, #10b981, #34d399)"
                            : "linear-gradient(90deg, #7c3aed, #a78bfa)",
                          borderRadius: "9999px",
                          transition: "width 0.5s ease",
                        }}
                      />
                    </div>
                    <p className="text-xs mt-1" style={{ color: "var(--color-fg-subtle)" }}>{file.progress}% complete</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </CreatorShell>
  );
}
