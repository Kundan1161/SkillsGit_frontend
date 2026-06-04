"use client";

import { useState } from "react";
import { Send, CheckCircle, XCircle, RefreshCw, FileText, Star } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const sampleQuestions = [
  "What's the best approach for zero-downtime Kubernetes deployments?",
  "How do I debug a CrashLoopBackOff in production?",
  "Explain the difference between HPA and VPA.",
];

const mockAnswer = {
  text: "For zero-downtime Kubernetes deployments, I recommend using a rolling update strategy with proper readiness probes. Here's my battle-tested approach:\n\n1. **Set maxUnavailable: 0** to ensure no pods go down before new ones are ready\n2. **Configure readiness probes** with realistic initialDelaySeconds (usually 30-60s for JVM apps)\n3. **Use PodDisruptionBudgets** to prevent voluntary disruptions during rollouts\n4. **Implement graceful shutdown** — handle SIGTERM in your app and drain connections properly\n\nI've used this pattern in 50+ production rollbacks at scale. The key insight is that readiness probes are often misconfigured — they check health but not actual traffic readiness.",
  confidence: 94,
  sources: [
    { file: "advanced-kubernetes-patterns.pdf", tokens: 2840, relevance: 96 },
    { file: "on-call-runbook.pdf",               tokens: 1200, relevance: 78 },
    { file: "architecture-decisions.md",          tokens: 640,  relevance: 62 },
  ],
};

export default function PreviewPage() {
  const [question, setQuestion]   = useState("");
  const [answered, setAnswered]   = useState(false);
  const [loading, setLoading]     = useState(false);

  const ask = (q?: string) => {
    const q2 = q ?? question;
    if (!q2.trim()) return;
    setQuestion(q2);
    setLoading(true);
    setTimeout(() => { setLoading(false); setAnswered(true); }, 1600);
  };

  return (
    <CreatorShell active="preview">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            AI <span className="gradient-text">Preview</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>Test your expert AI before publishing. Approve or improve responses.</p>
        </div>

        {/* Sample questions */}
        <div>
          <p className="tag-label mb-3">SAMPLE QUESTIONS</p>
          <div className="flex flex-col gap-2">
            {sampleQuestions.map((q) => (
              <button
                key={q}
                onClick={() => ask(q)}
                style={{ padding: "12px 16px", borderRadius: "0.875rem", border: "none", cursor: "pointer", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", textAlign: "left", fontSize: "0.85rem", color: "var(--color-fg-muted)", fontWeight: 500, transition: "all 0.2s ease" }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset)", borderRadius: "1.25rem", padding: "1rem", display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask your AI expert anything..."
            rows={2}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } }}
            style={{ flex: 1, background: "transparent", border: "none", outline: "none", resize: "none", fontSize: "0.9rem", color: "var(--color-fg)", fontFamily: "inherit" }}
          />
          <button
            onClick={() => ask()}
            disabled={!question.trim() || loading}
            style={{ width: 40, height: 40, borderRadius: "0.75rem", border: "none", cursor: "pointer", background: "linear-gradient(135deg,#7c3aed,#6366f1)", boxShadow: "4px 4px 10px rgba(124,58,237,0.35),-2px -2px 6px rgba(255,255,255,0.5)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, opacity: !question.trim() || loading ? 0.5 : 1 }}
          >
            <Send className="h-4 w-4 text-white" />
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="neu p-6 flex items-center gap-3">
            <RefreshCw className="h-5 w-5 animate-spin" style={{ color: "#7c3aed" }} />
            <span className="tag-label">Searching knowledge vault...</span>
          </div>
        )}

        {/* Answer */}
        {answered && !loading && (
          <div className="flex flex-col gap-4">
            <div className="neu-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg,#7c3aed,#6366f1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <span style={{ fontSize: "0.9rem" }}>🧠</span>
                  </div>
                  <span className="text-sm font-bold" style={{ color: "var(--color-fg)" }}>Your AI Expert</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5" style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "9999px" }}>
                  <Star className="h-3 w-3" style={{ fill: "#f59e0b", color: "#f59e0b" }} />
                  <span className="tag-label" style={{ color: "#10b981" }}>{mockAnswer.confidence}% confidence</span>
                </div>
              </div>

              <pre className="text-sm leading-relaxed whitespace-pre-wrap font-sans" style={{ color: "var(--color-fg)" }}>
                {mockAnswer.text}
              </pre>

              {/* Sources */}
              <div className="mt-5">
                <p className="tag-label mb-3">SOURCES CONSULTED</p>
                <div className="flex flex-col gap-2">
                  {mockAnswer.sources.map((s) => (
                    <div key={s.file} className="flex items-center gap-3 px-4 py-2.5" style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset-sm)", borderRadius: "0.75rem" }}>
                      <FileText className="h-3.5 w-3.5 shrink-0" style={{ color: "#7c3aed" }} />
                      <span className="text-xs flex-1 truncate font-medium" style={{ color: "var(--color-fg-muted)" }}>{s.file}</span>
                      <span className="tag-label" style={{ color: s.relevance > 85 ? "#10b981" : "#f59e0b" }}>{s.relevance}% match</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Approve / Improve */}
              <div className="mt-5 flex gap-3">
                <button
                  style={{ flex: 1, padding: "10px", borderRadius: "0.875rem", border: "none", cursor: "pointer", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", fontSize: "0.8rem", fontWeight: 700, color: "#10b981", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}
                >
                  <CheckCircle className="h-4 w-4" /> Approve response
                </button>
                <button
                  style={{ flex: 1, padding: "10px", borderRadius: "0.875rem", border: "none", cursor: "pointer", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", fontSize: "0.8rem", fontWeight: 700, color: "#f43f5e", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}
                >
                  <XCircle className="h-4 w-4" /> Needs improvement
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </CreatorShell>
  );
}
