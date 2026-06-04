import Link from "next/link";
import { Star, CheckCircle, MessageCircle, FileText, Video, Headphones, ArrowRight } from "lucide-react";

const sampleQuestions = [
  "How do I debug a pod stuck in CrashLoopBackOff?",
  "What's the best way to handle secrets in Kubernetes?",
  "Can you explain blue-green vs canary deployments?",
];

const vaultItems = [
  { icon: FileText, title: "Advanced Kubernetes Patterns", date: "Jun 1, 2024", type: "PDF" },
  { icon: Video, title: "DevOps Incident Response", date: "May 28, 2024", type: "Video" },
  { icon: Headphones, title: "Architecture Decisions Podcast", date: "May 15, 2024", type: "Audio" },
];

const included = [
  "Unlimited questions per month",
  "Access to full knowledge vault",
  "Source citations for every answer",
  "Priority response speed",
  "Cancel anytime",
];

export default function ExpertProfilePage() {
  return (
    <div style={{ background: "var(--color-bg)", minHeight: "100vh" }}>
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-16">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_340px]">

          {/* Main */}
          <div className="flex flex-col gap-10">
            {/* Hero */}
            <div className="neu-lg p-8 flex flex-col gap-6">
              <div className="flex items-start gap-6">
                <div
                  style={{
                    width: 120, height: 120, borderRadius: "50%",
                    background: "linear-gradient(135deg, #0ea5e9, #38bdf8)",
                    boxShadow: "var(--shadow-neu-lg)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: "white", fontWeight: 900, fontSize: 36,
                    flexShrink: 0,
                  }}
                >
                  MW
                </div>
                <div className="flex flex-col gap-2">
                  <div>
                    <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>Marcus Webb</h1>
                    <span className="tag-label">Kubernetes & DevOps</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-1">
                    <span className="neu-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>Engineering</span>
                    <span className="neu-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>12 years experience</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star key={i} className="h-4 w-4" style={{ color: "#f59e0b", fill: i < 5 ? "#f59e0b" : "none" }} />
                      ))}
                    </div>
                    <span className="text-sm font-semibold" style={{ color: "var(--color-fg-muted)" }}>4.8 (218 reviews)</span>
                  </div>
                </div>
              </div>

              <p className="text-base leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>
                12+ years architecting production Kubernetes clusters, CI/CD pipelines, and DevOps transformations for Fortune 500 companies. I've helped over 40 organizations migrate to cloud-native infrastructure and reduce incident response time by 70%.
              </p>

              {/* Sample questions */}
              <div>
                <p className="tag-label mb-3">Common Questions</p>
                <div className="flex flex-col gap-2">
                  {sampleQuestions.map((q) => (
                    <div key={q} className="neu-inset flex items-center gap-3 px-4 py-3" style={{ borderRadius: "var(--radius-lg)" }}>
                      <MessageCircle className="h-4 w-4 shrink-0" style={{ color: "#7c3aed" }} />
                      <span className="text-sm font-medium" style={{ color: "var(--color-fg-muted)" }}>{q}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Knowledge vault preview */}
            <div>
              <p className="tag-label mb-4">Knowledge Vault Preview</p>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                {vaultItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="neu-tile p-5 flex flex-col gap-3">
                      <div className="flex items-center gap-2">
                        <div className="neu-sm p-2 rounded-lg">
                          <Icon className="h-4 w-4" style={{ color: "#7c3aed" }} />
                        </div>
                        <span className="tag-label">{item.type}</span>
                      </div>
                      <p className="text-sm font-bold leading-snug" style={{ color: "var(--color-fg)" }}>{item.title}</p>
                      <span className="text-xs" style={{ color: "var(--color-fg-subtle)" }}>{item.date}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Subscription sidebar */}
          <aside className="flex flex-col gap-4">
            <div className="neu-lg p-7 flex flex-col gap-6 sticky top-24">
              <div className="text-center">
                <span className="text-4xl font-black gradient-text">$39</span>
                <span className="text-base" style={{ color: "var(--color-fg-subtle)" }}>/month</span>
                <p className="tag-label mt-1">Billed monthly · Cancel anytime</p>
              </div>

              <ul className="flex flex-col gap-2.5">
                {included.map(item => (
                  <li key={item} className="flex items-center gap-2.5 text-sm" style={{ color: "var(--color-fg-muted)" }}>
                    <CheckCircle className="h-4 w-4 shrink-0" style={{ color: "#7c3aed" }} />
                    {item}
                  </li>
                ))}
              </ul>

              <div className="flex flex-col gap-3">
                <Link
                  href="/chat/marcus-webb"
                  className="neu-btn-brand flex items-center justify-center gap-2 py-3.5 text-sm font-bold text-white w-full"
                >
                  Subscribe Now <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/chat/marcus-webb"
                  className="neu-btn flex items-center justify-center gap-2 py-3 text-sm font-semibold w-full"
                  style={{ color: "var(--color-fg-muted)" }}
                >
                  Preview Free
                </Link>
              </div>

              <p className="text-center text-xs" style={{ color: "var(--color-fg-subtle)" }}>
                3 free questions · No credit card needed
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
