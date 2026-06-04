"use client";

import { useState } from "react";
import { Eye, Globe, Lock, ArrowRight, Star } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

export default function ListingPage() {
  const [status, setStatus] = useState<"draft" | "live">("live");
  const [price, setPrice]   = useState("29");
  const [title, setTitle]   = useState("Marcus Webb — Senior DevOps & Kubernetes Expert");
  const [tagline, setTagline] = useState("8 years of production Kubernetes war stories. On-call patterns, SRE frameworks, cost optimization.");

  return (
    <CreatorShell active="listing">
      <div className="flex flex-col gap-8">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
              Manage <span className="gradient-text">Listing</span>
            </h1>
            <p className="mt-1 text-sm" style={{ color: "var(--color-fg-muted)" }}>Control how buyers see your expert AI on the marketplace.</p>
          </div>
          {/* Status toggle */}
          <div className="flex gap-2">
            {(["draft", "live"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStatus(s)}
                style={{
                  padding: "10px 20px", borderRadius: "9999px", border: "none", cursor: "pointer",
                  fontSize: "0.78rem", fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase",
                  background: "var(--color-bg)",
                  boxShadow: status === s ? "var(--shadow-neu-inset-sm)" : "var(--shadow-neu-sm)",
                  color: status === s ? "#7c3aed" : "var(--color-fg-muted)",
                  transition: "all 0.2s ease",
                  display: "flex", alignItems: "center", gap: "0.4rem",
                }}
              >
                {s === "live" ? <Globe className="h-3.5 w-3.5" /> : <Lock className="h-3.5 w-3.5" />}
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_340px]">
          {/* Form */}
          <div className="flex flex-col gap-5">
            {[
              { label: "LISTING TITLE", value: title, setter: setTitle, multiline: false },
              { label: "TAGLINE", value: tagline, setter: setTagline, multiline: true },
            ].map(({ label, value, setter, multiline }) => (
              <div key={label}>
                <p className="tag-label mb-2">{label}</p>
                {multiline ? (
                  <textarea
                    value={value}
                    onChange={e => setter(e.target.value)}
                    rows={3}
                    style={{ width: "100%", padding: "14px 16px", borderRadius: "1rem", border: "none", outline: "none", resize: "vertical", fontSize: "0.9rem", fontFamily: "inherit", color: "var(--color-fg)", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset)", display: "block" }}
                  />
                ) : (
                  <input
                    value={value}
                    onChange={e => setter(e.target.value)}
                    style={{ width: "100%", padding: "14px 16px", borderRadius: "1rem", border: "none", outline: "none", fontSize: "0.9rem", fontFamily: "inherit", color: "var(--color-fg)", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset)", display: "block" }}
                  />
                )}
              </div>
            ))}

            {/* Price */}
            <div>
              <p className="tag-label mb-2">MONTHLY PRICE (USD)</p>
              <div className="flex items-center gap-3">
                <div style={{ display: "flex", alignItems: "center", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset)", borderRadius: "1rem", padding: "12px 16px", gap: "4px" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 900, color: "#7c3aed" }}>$</span>
                  <input
                    type="number"
                    value={price}
                    onChange={e => setPrice(e.target.value)}
                    min={1}
                    style={{ width: 80, background: "transparent", border: "none", outline: "none", fontSize: "1.3rem", fontWeight: 900, color: "var(--color-fg)", fontFamily: "inherit" }}
                  />
                  <span style={{ fontSize: "0.8rem", color: "var(--color-fg-subtle)", fontWeight: 600 }}>/mo</span>
                </div>
                <span style={{ fontSize: "0.8rem", color: "var(--color-fg-muted)" }}>
                  You earn <strong style={{ color: "#10b981" }}>${Math.round(Number(price) * 0.75)}</strong> per subscriber/mo (75% share)
                </span>
              </div>
            </div>

            <button
              style={{ padding: "14px 28px", borderRadius: "1rem", border: "none", cursor: "pointer", background: "linear-gradient(135deg,#7c3aed,#6366f1)", boxShadow: "6px 6px 16px rgba(124,58,237,0.35),-2px -2px 8px rgba(255,255,255,0.5)", fontSize: "0.9rem", fontWeight: 800, color: "white", display: "flex", alignItems: "center", gap: "0.5rem", width: "fit-content" }}
            >
              Save & publish <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          {/* Preview card */}
          <div>
            <p className="tag-label mb-3">MARKETPLACE PREVIEW</p>
            <div style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-md)", borderRadius: "1.5rem", overflow: "hidden" }}>
              <div style={{ height: 100, background: "linear-gradient(135deg,rgba(124,58,237,0.15),rgba(99,102,241,0.08))", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <div style={{ width: 64, height: 64, borderRadius: "50%", background: "linear-gradient(135deg,#7c3aed,#6366f1)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "var(--shadow-neu-md)", fontSize: "1.6rem" }}>🧠</div>
              </div>
              <div style={{ padding: "1.25rem" }}>
                <p className="font-black text-sm" style={{ letterSpacing: "-0.02em", color: "var(--color-fg)" }}>{title}</p>
                <p className="text-xs mt-1 leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>{tagline.slice(0, 80)}...</p>
                <div className="flex items-center gap-1 mt-2">
                  {[1,2,3,4,5].map(i => <Star key={i} className="h-3 w-3" style={{ fill: "#f59e0b", color: "#f59e0b" }} />)}
                  <span className="text-xs ml-1 font-bold" style={{ color: "var(--color-fg)" }}>4.9</span>
                </div>
                <div className="flex items-center justify-between mt-3">
                  <div style={{ background: "var(--color-bg)", boxShadow: "var(--shadow-neu-inset-sm)", borderRadius: "9999px", padding: "4px 12px" }}>
                    <span className="text-sm font-black" style={{ color: "#059669" }}>${price}/mo</span>
                  </div>
                  <button style={{ padding: "6px 14px", borderRadius: "9999px", border: "none", cursor: "pointer", background: "linear-gradient(135deg,#7c3aed,#6366f1)", fontSize: "0.7rem", fontWeight: 700, color: "white" }}>
                    Subscribe
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </CreatorShell>
  );
}
