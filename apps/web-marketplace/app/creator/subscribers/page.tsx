import { Users, TrendingUp, TrendingDown, Star } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const subscribers = [
  { name: "Alex Thompson",  plan: "Monthly", since: "Jan 2025",  mrr: "$29", avatar: "#7c3aed", initials: "AT", questions: 142, rating: 5 },
  { name: "Maria Lopez",    plan: "Monthly", since: "Feb 2025",  mrr: "$29", avatar: "#3b82f6", initials: "ML", questions: 89,  rating: 5 },
  { name: "Sam Kim",        plan: "Monthly", since: "Mar 2025",  mrr: "$29", avatar: "#10b981", initials: "SK", questions: 203, rating: 4 },
  { name: "Priya Patel",    plan: "Monthly", since: "Mar 2025",  mrr: "$29", avatar: "#f59e0b", initials: "PP", questions: 67,  rating: 5 },
  { name: "James O'Brien",  plan: "Monthly", since: "Apr 2025",  mrr: "$29", avatar: "#f43f5e", initials: "JO", questions: 31,  rating: 4 },
  { name: "Yuki Tanaka",    plan: "Monthly", since: "May 2025",  mrr: "$29", avatar: "#06b6d4", initials: "YT", questions: 18,  rating: 5 },
];

const metrics = [
  { label: "Active Subscribers", value: "312",    icon: Users,        color: "#7c3aed", trend: "+14 this month" },
  { label: "MRR",                value: "$4,680",  icon: TrendingUp,   color: "#10b981", trend: "+$406 vs last month" },
  { label: "Churn Rate",         value: "2.1%",    icon: TrendingDown, color: "#f43f5e", trend: "-0.3% improvement" },
  { label: "Avg. Questions/Sub", value: "27",      icon: Star,         color: "#f59e0b", trend: "per month" },
];

export default function SubscribersPage() {
  return (
    <CreatorShell active="subscribers">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            <span className="gradient-text">Subscribers</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>Everyone paying for access to your expert AI.</p>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {metrics.map((m) => {
            const Icon = m.icon;
            return (
              <div key={m.label} className="neu p-5 flex flex-col gap-3">
                <div style={{ width: 36, height: 36, borderRadius: "0.75rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon className="h-4.5 w-4.5 h-[18px] w-[18px]" style={{ color: m.color }} />
                </div>
                <div>
                  <span className="tag-label block mb-1">{m.label}</span>
                  <span className="text-2xl font-black" style={{ color: m.color, letterSpacing: "-0.04em" }}>{m.value}</span>
                  <span className="block text-xs mt-0.5" style={{ color: "var(--color-fg-subtle)" }}>{m.trend}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Subscriber list */}
        <div className="neu-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-black" style={{ letterSpacing: "-0.02em", color: "var(--color-fg)" }}>Recent Subscribers</h2>
            <span className="tag-label">Showing 6 of 312</span>
          </div>

          {/* Table header */}
          <div className="grid grid-cols-[auto_1fr_100px_80px_80px_80px] gap-4 px-3 mb-3">
            {["", "Subscriber", "Plan", "Since", "MRR", "Questions"].map((h) => (
              <span key={h} className="tag-label">{h}</span>
            ))}
          </div>

          <div className="flex flex-col gap-2">
            {subscribers.map((s) => (
              <div
                key={s.name}
                style={{ display: "grid", gridTemplateColumns: "auto 1fr 100px 80px 80px 80px", gap: "1rem", alignItems: "center", padding: "12px", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-xs)", borderRadius: "0.875rem" }}
              >
                {/* Avatar */}
                <div style={{ width: 36, height: 36, borderRadius: "50%", background: `linear-gradient(135deg,${s.avatar},${s.avatar}88)`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.65rem", fontWeight: 900, color: "white" }}>
                  {s.initials}
                </div>
                {/* Name + stars */}
                <div>
                  <p className="text-sm font-bold" style={{ color: "var(--color-fg)" }}>{s.name}</p>
                  <div className="flex items-center gap-0.5 mt-0.5">
                    {[1,2,3,4,5].map(i => (
                      <Star key={i} className="h-2.5 w-2.5" style={{ fill: i <= s.rating ? "#f59e0b" : "transparent", color: "#f59e0b" }} />
                    ))}
                  </div>
                </div>
                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--color-fg-muted)" }}>{s.plan}</span>
                <span style={{ fontSize: "0.75rem", color: "var(--color-fg-subtle)" }}>{s.since}</span>
                <span style={{ fontSize: "0.85rem", fontWeight: 900, color: "#10b981" }}>{s.mrr}</span>
                <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--color-fg)" }}>{s.questions}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </CreatorShell>
  );
}
