"use client";
import { useState } from "react";
import { Send, Brain, ChevronRight, Shield } from "lucide-react";

const initialMessages = [
  {
    role: "user" as const,
    content: "How do I debug a Kubernetes pod that's in CrashLoopBackOff?",
    time: "2:34 PM",
  },
  {
    role: "ai" as const,
    content: `A CrashLoopBackOff means your pod is starting, crashing, and Kubernetes keeps restarting it. Here's my systematic approach:

**1. Check the logs first**
\`kubectl logs <pod-name> --previous\`
The \`--previous\` flag shows logs from the last crashed container — crucial for seeing the actual error.

**2. Describe the pod**
\`kubectl describe pod <pod-name>\`
Look at the Events section at the bottom. It shows OOMKilled (memory), exit codes, and readiness probe failures.

**3. Common causes:**
- Exit code 1: Application error — check your app logs
- Exit code 137: OOMKilled — increase memory limits
- Exit code 139: Segfault — check for corrupted images
- Readiness probe failing — your app isn't starting fast enough

**4. Quick fix for investigation:**
Override the command temporarily to keep it running: \`command: ["sleep", "3600"]\` then exec into the container to debug interactively.`,
    time: "2:34 PM",
    sources: [
      { title: "advanced-kubernetes-patterns.pdf", confidence: 94 },
      { title: "on-call-runbook.pdf", confidence: 87 },
      { title: "devops-incident-response.mp4", confidence: 72 },
    ],
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [expandedSources, setExpandedSources] = useState<number[]>([1]);

  const toggleSources = (idx: number) => {
    setExpandedSources(prev => prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]);
  };

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: "user", content: input, time: "Now" }]);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ height: "calc(100vh - 64px)", display: "flex", flexDirection: "column", background: "var(--color-bg)" }}>

      {/* Header strip */}
      <div className="neu flex items-center gap-4 px-6 py-4" style={{ borderRadius: 0, boxShadow: "0 4px 16px rgba(166,162,153,0.25)" }}>
        <div style={{ width: 44, height: 44, borderRadius: "50%", background: "linear-gradient(135deg, #0ea5e9, #38bdf8)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 900, fontSize: 14, flexShrink: 0 }}>
          MW
        </div>
        <div>
          <h2 className="text-sm font-bold" style={{ color: "var(--color-fg)" }}>Marcus Webb AI</h2>
          <div className="flex items-center gap-1.5">
            <Shield className="h-3 w-3" style={{ color: "#10b981" }} />
            <span className="tag-label">Powered by verified knowledge vault</span>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="h-2 w-2 rounded-full animate-neu-pulse" style={{ background: "#10b981" }} />
          <span className="text-xs font-semibold" style={{ color: "#10b981" }}>Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6" style={{ boxShadow: "var(--shadow-neu-inset)", margin: "12px", borderRadius: "var(--radius-2xl)" }}>
        <div className="mx-auto max-w-3xl flex flex-col gap-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "user" ? (
                <div
                  style={{
                    background: "linear-gradient(135deg, #7c3aed, #6366f1)",
                    borderRadius: "20px 20px 4px 20px",
                    padding: "12px 16px",
                    maxWidth: "70%",
                    boxShadow: "6px 6px 16px rgba(124,58,237,0.3)",
                  }}
                >
                  <p className="text-sm text-white leading-relaxed">{msg.content}</p>
                  <p className="text-xs text-white/60 mt-1 text-right">{msg.time}</p>
                </div>
              ) : (
                <div style={{ maxWidth: "82%" }} className="flex flex-col gap-2">
                  <div className="neu p-4" style={{ borderRadius: "4px 20px 20px 20px" }}>
                    <div className="flex items-center gap-2 mb-3">
                      <Brain className="h-4 w-4" style={{ color: "#7c3aed" }} />
                      <span className="tag-label gradient-text">Marcus Webb AI</span>
                    </div>
                    <div className="text-sm leading-relaxed whitespace-pre-line" style={{ color: "var(--color-fg)" }}>
                      {msg.content}
                    </div>
                    <p className="text-xs mt-2" style={{ color: "var(--color-fg-subtle)" }}>{msg.time}</p>
                  </div>

                  {/* Sources */}
                  {msg.sources && (
                    <div className="neu-inset p-3" style={{ borderRadius: "var(--radius-lg)" }}>
                      <button
                        onClick={() => toggleSources(idx)}
                        className="flex items-center gap-2 w-full text-left"
                      >
                        <span className="tag-label">3 sources cited</span>
                        <ChevronRight
                          className="h-3 w-3 ml-auto transition-transform"
                          style={{ color: "var(--color-fg-subtle)", transform: expandedSources.includes(idx) ? "rotate(90deg)" : "none" }}
                        />
                      </button>
                      {expandedSources.includes(idx) && (
                        <div className="flex flex-col gap-2 mt-3">
                          {msg.sources.map((src, si) => (
                            <div key={si} className="flex items-center justify-between">
                              <span className="text-xs" style={{ color: "var(--color-fg-muted)" }}>{src.title}</span>
                              <span className="text-xs font-bold" style={{ color: src.confidence > 85 ? "#10b981" : "#f59e0b" }}>{src.confidence}%</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Input area */}
      <div className="p-4">
        <div className="mx-auto max-w-3xl">
          <div className="neu flex items-end gap-3 p-3" style={{ borderRadius: "var(--radius-xl)" }}>
            <div className="flex-1 neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-lg)" }}>
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Marcus anything about Kubernetes & DevOps..."
                rows={1}
                className="w-full bg-transparent text-sm outline-none resize-none"
                style={{ color: "var(--color-fg)", minHeight: 24 }}
              />
            </div>
            <button
              onClick={handleSend}
              className="neu-btn-brand flex h-10 w-10 items-center justify-center shrink-0"
              style={{ borderRadius: "50%" }}
            >
              <Send className="h-4 w-4 text-white" />
            </button>
          </div>
          <p className="text-center text-xs mt-2" style={{ color: "var(--color-fg-subtle)" }}>
            Answers sourced from Marcus&apos;s verified knowledge vault · 3 sources cited
          </p>
        </div>
      </div>
    </div>
  );
}
