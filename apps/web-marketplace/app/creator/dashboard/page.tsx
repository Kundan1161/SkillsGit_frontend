import { TrendingUp, MessageCircle, Clock } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const primaryStats = [
  { label: "Files Uploaded", value: "47", suffix: "", color: "#7c3aed" },
  { label: "AI Readiness", value: "94", suffix: "%", color: "#10b981" },
  { label: "Active Subscribers", value: "312", suffix: "", color: "#0ea5e9" },
  { label: "Monthly Revenue", value: "$4,680", suffix: "", color: "#f59e0b" },
];

const secondaryStats = [
  { label: "Questions Answered", value: "8,420" },
  { label: "Vault Completion", value: "87%" },
];

const recentActivity = [
  { question: "What's the best approach for zero-downtime Kubernetes deployments?", time: "2 min ago", subscriber: "Alex T." },
  { question: "How do I configure Prometheus alerting for pod CPU limits?", time: "14 min ago", subscriber: "Maria L." },
  { question: "Can you explain the difference between DaemonSet and Deployment?", time: "31 min ago", subscriber: "Sam K." },
];

export default function CreatorDashboard() {
  return (
    <CreatorShell>
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            Creator <span className="gradient-text">Dashboard</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>Your AI expert is live and earning.</p>
        </div>

        {/* Primary stats */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {primaryStats.map((stat) => (
            <div key={stat.label} className="neu p-6 flex flex-col gap-2">
              <span className="tag-label">{stat.label}</span>
              <span className="text-3xl font-black tracking-tight" style={{ color: stat.color }}>
                {stat.value}{stat.suffix}
              </span>
            </div>
          ))}
        </div>

        {/* Secondary stats */}
        <div className="grid grid-cols-2 gap-4">
          {secondaryStats.map((stat) => (
            <div key={stat.label} className="neu p-5 flex items-center gap-4">
              <div className="neu-inset p-3 rounded-xl">
                <TrendingUp className="h-5 w-5" style={{ color: "#7c3aed" }} />
              </div>
              <div>
                <span className="tag-label block">{stat.label}</span>
                <span className="text-2xl font-black gradient-text">{stat.value}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Recent activity */}
        <div className="neu-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold" style={{ color: "var(--color-fg)" }}>Recent Questions</h2>
            <span className="tag-label">Live feed</span>
          </div>
          <div className="flex flex-col gap-4">
            {recentActivity.map((item, i) => (
              <div key={i} className="neu-inset p-4 flex flex-col gap-2" style={{ borderRadius: "var(--radius-lg)" }}>
                <div className="flex items-start gap-3">
                  <MessageCircle className="h-4 w-4 mt-0.5 shrink-0" style={{ color: "#7c3aed" }} />
                  <p className="text-sm font-medium leading-snug flex-1" style={{ color: "var(--color-fg)" }}>{item.question}</p>
                </div>
                <div className="flex items-center gap-3 pl-7">
                  <span className="text-xs font-semibold" style={{ color: "var(--color-fg-subtle)" }}>{item.subscriber}</span>
                  <span className="h-1 w-1 rounded-full" style={{ background: "var(--color-fg-subtle)" }} />
                  <Clock className="h-3 w-3" style={{ color: "var(--color-fg-subtle)" }} />
                  <span className="text-xs" style={{ color: "var(--color-fg-subtle)" }}>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </CreatorShell>
  );
}
