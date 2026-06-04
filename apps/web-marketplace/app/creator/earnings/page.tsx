import { TrendingUp, Users, DollarSign } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const metrics = [
  { label: "Monthly Recurring Revenue", value: "$4,680", icon: TrendingUp, color: "#7c3aed" },
  { label: "Active Subscribers", value: "312", icon: Users, color: "#10b981" },
  { label: "Churn Rate", value: "2.1%", icon: TrendingUp, color: "#f59e0b" },
  { label: "Available Balance", value: "$3,420", icon: DollarSign, color: "#0ea5e9", action: true },
];

const monthlyData = [
  { month: "Jan", amount: 1200 },
  { month: "Feb", amount: 1800 },
  { month: "Mar", amount: 2100 },
  { month: "Apr", amount: 2800 },
  { month: "May", amount: 3400 },
  { month: "Jun", amount: 4680 },
];

const maxAmount = Math.max(...monthlyData.map(d => d.amount));

const subscribers = [
  { initials: "AT", name: "Alex Thompson", plan: "Monthly", since: "Mar 2024", mrr: "$39" },
  { initials: "ML", name: "Maria Lopez", plan: "Annual", since: "Jan 2024", mrr: "$32" },
  { initials: "SK", name: "Sam Kim", plan: "Monthly", since: "Apr 2024", mrr: "$39" },
  { initials: "RN", name: "Rachel Nash", plan: "Annual", since: "Feb 2024", mrr: "$32" },
  { initials: "JB", name: "Jordan Blake", plan: "Monthly", since: "May 2024", mrr: "$39" },
];

export default function EarningsPage() {
  return (
    <CreatorShell active="earnings">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10">
          <span className="tag-label block mb-2">Revenue</span>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            Earnings <span className="gradient-text">Dashboard</span>
          </h1>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-4">
          {metrics.map((m) => {
            const Icon = m.icon;
            return (
              <div key={m.label} className="neu p-6 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <Icon className="h-5 w-5" style={{ color: m.color }} />
                  {m.action && (
                    <button className="neu-btn-brand px-3 py-1.5 text-xs font-bold text-white">
                      Withdraw
                    </button>
                  )}
                </div>
                <div>
                  <span className="text-2xl font-black tracking-tight" style={{ color: m.color }}>{m.value}</span>
                  <p className="tag-label mt-1">{m.label}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Revenue chart */}
        <div className="neu-lg p-8 mb-8">
          <h2 className="text-base font-bold mb-8" style={{ color: "var(--color-fg)" }}>Revenue Growth</h2>
          <div className="flex items-end gap-4" style={{ height: 200 }}>
            {monthlyData.map((d) => {
              const heightPct = (d.amount / maxAmount) * 100;
              return (
                <div key={d.month} className="flex-1 flex flex-col items-center gap-2">
                  <span className="text-xs font-bold gradient-text">${(d.amount / 1000).toFixed(1)}k</span>
                  <div className="w-full flex items-end" style={{ height: 160 }}>
                    <div
                      className="w-full"
                      style={{
                        height: `${heightPct}%`,
                        background: "linear-gradient(180deg, #7c3aed, #a78bfa)",
                        borderRadius: "8px 8px 0 0",
                        boxShadow: "4px 4px 12px rgba(124,58,237,0.3), -2px -2px 6px rgba(255,255,255,0.5)",
                        transition: "height 0.6s ease",
                      }}
                    />
                  </div>
                  <span className="tag-label">{d.month}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Subscribers table */}
        <div className="neu-lg p-6">
          <h2 className="text-base font-bold mb-6" style={{ color: "var(--color-fg)" }}>Subscribers</h2>
          <div className="flex flex-col gap-3">
            <div className="grid grid-cols-5 gap-4 px-4 pb-3" style={{ borderBottom: "1px solid rgba(124,58,237,0.1)" }}>
              {["Subscriber", "Plan", "Since", "MRR", ""].map(h => (
                <span key={h} className="tag-label">{h}</span>
              ))}
            </div>
            {subscribers.map((s, i) => (
              <div key={i} className="neu-inset grid grid-cols-5 gap-4 items-center px-4 py-3" style={{ borderRadius: "var(--radius-lg)" }}>
                <div className="flex items-center gap-3">
                  <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg, #7c3aed, #6366f1)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 700, fontSize: 11, flexShrink: 0 }}>
                    {s.initials}
                  </div>
                  <span className="text-sm font-semibold" style={{ color: "var(--color-fg)" }}>{s.name}</span>
                </div>
                <span className="text-xs font-semibold" style={{ color: "var(--color-fg-muted)" }}>{s.plan}</span>
                <span className="text-xs" style={{ color: "var(--color-fg-subtle)" }}>{s.since}</span>
                <span className="text-sm font-bold gradient-text">{s.mrr}</span>
                <span />
              </div>
            ))}
          </div>
        </div>
      </div>
    </CreatorShell>
  );
}
