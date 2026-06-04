import Link from "next/link";
import { Search, Star, ArrowRight, MessageCircle } from "lucide-react";

const experts = [
  {
    name: "Dr. Sarah Chen",
    specialty: "Diagnostic Medicine",
    category: "Healthcare",
    years: 18,
    rating: 4.9,
    reviews: 342,
    price: 49,
    gradient: "linear-gradient(135deg, #7c3aed, #a78bfa)",
    initials: "SC",
    handle: "dr-sarah-chen",
  },
  {
    name: "Marcus Webb",
    specialty: "Kubernetes & DevOps",
    category: "Engineering",
    years: 12,
    rating: 4.8,
    reviews: 218,
    price: 39,
    gradient: "linear-gradient(135deg, #0ea5e9, #38bdf8)",
    initials: "MW",
    handle: "marcus-webb",
  },
  {
    name: "Elena Rodriguez",
    specialty: "UX Research",
    category: "Design",
    years: 9,
    rating: 4.9,
    reviews: 187,
    price: 29,
    gradient: "linear-gradient(135deg, #f59e0b, #fbbf24)",
    initials: "ER",
    handle: "elena-rodriguez",
  },
  {
    name: "James Park",
    specialty: "Corporate Finance",
    category: "Finance",
    years: 15,
    rating: 4.7,
    reviews: 291,
    price: 59,
    gradient: "linear-gradient(135deg, #10b981, #34d399)",
    initials: "JP",
    handle: "james-park",
  },
  {
    name: "Aisha Mohammed",
    specialty: "Contract Law",
    category: "Legal",
    years: 11,
    rating: 4.8,
    reviews: 156,
    price: 69,
    gradient: "linear-gradient(135deg, #ef4444, #f87171)",
    initials: "AM",
    handle: "aisha-mohammed",
  },
  {
    name: "Chef Antoine",
    specialty: "French Culinary Arts",
    category: "Culinary",
    years: 22,
    rating: 5.0,
    reviews: 89,
    price: 24,
    gradient: "linear-gradient(135deg, #f97316, #fb923c)",
    initials: "CA",
    handle: "chef-antoine",
  },
];

const filters = ["All", "Healthcare", "Engineering", "Design", "Finance", "Legal", "Culinary"];

export default function ExplorePage() {
  return (
    <div style={{ background: "var(--color-bg)", minHeight: "100vh" }}>
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-16">

        {/* Header */}
        <div className="mb-12">
          <span className="tag-label block mb-3">Marketplace</span>
          <h1 className="text-4xl font-black tracking-[-0.04em] lg:text-5xl" style={{ color: "var(--color-fg)" }}>
            Explore <span className="gradient-text">Expert AIs</span>
          </h1>
          <p className="mt-3 text-lg" style={{ color: "var(--color-fg-muted)" }}>
            Chat with AI experts built from verified professional knowledge vaults.
          </p>
        </div>

        {/* Search */}
        <div className="mb-8 relative">
          <div className="neu-inset flex items-center gap-3 px-5 py-4" style={{ borderRadius: "var(--radius-xl)" }}>
            <Search className="h-5 w-5 shrink-0" style={{ color: "var(--color-fg-subtle)" }} />
            <input
              type="text"
              placeholder="Search experts by name, specialty, or topic..."
              className="flex-1 bg-transparent text-base outline-none"
              style={{ color: "var(--color-fg)" }}
            />
          </div>
        </div>

        {/* Filter chips */}
        <div className="mb-10 flex flex-wrap gap-3">
          {filters.map((f, i) => (
            <button
              key={f}
              className={i === 0 ? "neu-btn-brand px-5 py-2 text-sm font-semibold text-white" : "neu-btn px-5 py-2 text-sm font-semibold"}
              style={i !== 0 ? { color: "var(--color-fg-muted)" } : {}}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Expert grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {experts.map((expert) => (
            <div key={expert.handle} className="neu-card p-6 flex flex-col gap-5">
              {/* Avatar + header */}
              <div className="flex items-start gap-4">
                <div
                  style={{
                    width: 64, height: 64, borderRadius: "50%",
                    background: expert.gradient,
                    boxShadow: "var(--shadow-neu-sm)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: "white", fontWeight: 900, fontSize: 20,
                    flexShrink: 0,
                  }}
                >
                  {expert.initials}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-bold leading-tight" style={{ color: "var(--color-fg)" }}>{expert.name}</h3>
                  <span className="tag-label mt-1 block">{expert.specialty}</span>
                  <div className="mt-1.5 flex items-center gap-1.5">
                    <div className="flex items-center gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className="h-3 w-3"
                          style={{ color: i < Math.floor(expert.rating) ? "#f59e0b" : "var(--color-fg-subtle)", fill: i < Math.floor(expert.rating) ? "#f59e0b" : "none" }}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-semibold" style={{ color: "var(--color-fg-muted)" }}>
                      {expert.rating} ({expert.reviews})
                    </span>
                  </div>
                </div>
              </div>

              {/* Meta */}
              <div className="flex flex-wrap gap-2">
                <span className="neu-inset-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>
                  {expert.category}
                </span>
                <span className="neu-inset-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>
                  {expert.years} yrs experience
                </span>
              </div>

              {/* Price */}
              <div className="flex items-center justify-between">
                <div
                  className="neu-inset px-4 py-2"
                  style={{ borderRadius: "9999px" }}
                >
                  <span className="text-lg font-black gradient-text">${expert.price}</span>
                  <span className="text-xs ml-1" style={{ color: "var(--color-fg-subtle)" }}>/mo</span>
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3">
                <Link
                  href={`/expert/${expert.handle}`}
                  className="neu-btn-brand flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-bold text-white"
                >
                  Subscribe
                </Link>
                <Link
                  href={`/chat/${expert.handle}`}
                  className="neu-btn flex items-center gap-1.5 px-4 py-2.5 text-sm font-semibold"
                  style={{ color: "var(--color-fg-muted)" }}
                >
                  <MessageCircle className="h-4 w-4" />
                  Preview AI
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
